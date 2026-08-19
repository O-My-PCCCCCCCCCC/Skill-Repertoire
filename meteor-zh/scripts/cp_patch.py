# -*- coding: utf-8 -*-
"""Constant-pool string literal patcher for Meteor Client class files.

Parses JVM class files (up to Java 25), identifies string literals, and rewrites
them from a translation mapping without altering the class structure.

SAFETY: A CONSTANT_Utf8 entry is only translated when it is referenced by at
least one CONSTANT_String (i.e. it is a string literal used via `ldc`) AND is
NOT referenced by any structural element (field/method name, descriptor, class
name, method type, module/package name). javac deduplicates identical Utf8
strings, so an enum constant name like "EGap" and the literal "EGap" often share
ONE Utf8 entry; translating that entry would corrupt the field name and can even
create duplicate field names (ClassFormatError). We therefore skip shared entries.
"""
import struct


class ClassFile:
    def __init__(self, data):
        self.data = data
        self.major = struct.unpack('>H', data[6:8])[0]
        self.cp_count = struct.unpack('>H', data[8:10])[0]
        self.cp_end = None
        self.utf8 = {}       # cp index -> (start, end, value)
        self._literal_refs = {}   # cp index -> count of CONSTANT_String refs
        self._structural_refs = {}  # cp index -> count of structural refs
        self._parse()

    def _ref(self, idx, structural):
        if structural:
            self._structural_refs[idx] = self._structural_refs.get(idx, 0) + 1
        else:
            self._literal_refs[idx] = self._literal_refs.get(idx, 0) + 1

    def _parse(self):
        idx = 10
        count = self.cp_count
        i = 1
        while i < count:
            tag = self.data[idx]
            if tag == 1:
                ln = struct.unpack('>H', self.data[idx+1:idx+3])[0]
                start = idx
                end = idx + 3 + ln
                val = self.data[idx+3:end].decode('utf-8', 'replace')
                self.utf8[i] = (start, end, val)
                idx = end
            elif tag == 7:      # Class -> Utf8 (structural)
                self._ref(struct.unpack('>H', self.data[idx+1:idx+3])[0], True)
                idx += 3
            elif tag == 8:      # String -> Utf8 (literal)
                self._ref(struct.unpack('>H', self.data[idx+1:idx+3])[0], False)
                idx += 3
            elif tag == 9 or tag == 10 or tag == 11:  # Field/Method/InterfaceMethod ref -> Class + NameAndType
                idx += 5
            elif tag == 12:     # NameAndType -> Utf8 name + Utf8 desc (structural)
                n = struct.unpack('>H', self.data[idx+1:idx+3])[0]
                d = struct.unpack('>H', self.data[idx+3:idx+5])[0]
                self._ref(n, True)
                self._ref(d, True)
                idx += 5
            elif tag == 15:     # MethodHandle
                idx += 4
            elif tag == 16:     # MethodType -> Utf8 desc (structural)
                self._ref(struct.unpack('>H', self.data[idx+1:idx+3])[0], True)
                idx += 3
            elif tag == 17 or tag == 18:  # Dynamic / InvokeDynamic -> NameAndType
                idx += 5
            elif tag == 19 or tag == 20:  # Module / Package -> Utf8 (structural)
                self._ref(struct.unpack('>H', self.data[idx+1:idx+3])[0], True)
                idx += 3
            elif tag in (3, 4):
                idx += 5
            elif tag in (5, 6):
                idx += 9
                i += 1
            else:
                raise ValueError(f'unknown cp tag {tag} at index {i}')
            i += 1
        self.cp_end = idx

    def _translatable(self, uidx):
        return uidx in self._literal_refs and uidx not in self._structural_refs

    def string_literals(self):
        """Values of Utf8 entries that are safe to translate (pure literals)."""
        return {self.utf8[i][2] for i in self.utf8 if self._translatable(i)}

    def literal_counts(self):
        """value -> number of translatable (pure-literal) Utf8 entries with that value."""
        counts = {}
        for i in self.utf8:
            if self._translatable(i):
                v = self.utf8[i][2]
                counts[v] = counts.get(v, 0) + 1
        return counts

    def _parse_names(self):
        """Parse fields/methods tables to learn which Utf8 indices are field/method names."""
        idx = self.cp_end
        idx += 2  # access flags
        idx += 2  # this_class
        idx += 2  # super_class
        ifc = struct.unpack('>H', self.data[idx:idx+2])[0]
        idx += 2 + 2 * ifc
        # fields
        fc = struct.unpack('>H', self.data[idx:idx+2])[0]
        idx += 2
        field_name_idx = set()
        for _ in range(fc):
            acc, ni, di = struct.unpack('>HHH', self.data[idx:idx+6])
            field_name_idx.add(ni)
            idx += 6
            ac = struct.unpack('>H', self.data[idx:idx+2])[0]
            idx += 2
            for _ in range(ac):
                idx += 2
                alen = struct.unpack('>I', self.data[idx:idx+4])[0]
                idx += 4 + alen
        mc = struct.unpack('>H', self.data[idx:idx+2])[0]
        idx += 2
        method_name_idx = set()
        for _ in range(mc):
            acc, ni, di = struct.unpack('>HHH', self.data[idx:idx+6])
            method_name_idx.add(ni)
            idx += 6
            ac = struct.unpack('>H', self.data[idx:idx+2])[0]
            idx += 2
            for _ in range(ac):
                idx += 2
                alen = struct.unpack('>I', self.data[idx:idx+4])[0]
                idx += 4 + alen
        self._field_name_idx = field_name_idx
        self._method_name_idx = method_name_idx

    def to_bytes_force(self, mapping, force_map):
        """Translate pure literals from `mapping`; additionally translate ALL Utf8
        entries (literal OR structural) whose value is a key of `force_map`, unless
        that would create a duplicate field/method name in this class (skip those)."""
        if not hasattr(self, '_field_name_idx'):
            self._parse_names()

        # Per-index decision: resulting value for each Utf8 entry
        def result_value(i, val):
            if i in force_decide:
                return force_decide[i]
            if self._translatable(i):
                return mapping.get(val, val)
            return val

        force_decide = {}
        for i, (_, _, val) in self.utf8.items():
            if val in force_map:
                force_decide[i] = force_map[val]

        # Detect duplicate field/method names introduced by force translation
        from collections import Counter
        skip = set()
        for idx_set, result_of in (
            (self._field_name_idx, lambda i: force_decide.get(i, self.utf8[i][2])),
            (self._method_name_idx, lambda i: force_decide.get(i, self.utf8[i][2])),
        ):
            names = [result_of(i) for i in idx_set]
            dups = {k for k, v in Counter(names).items() if v > 1}
            for i in idx_set:
                if i in force_decide and force_decide[i] in dups:
                    skip.add(i)

        # Rebuild the class file, translating per the decision (skip for dup-safe force)
        parts = []
        i = 1
        idx = 10
        count = self.cp_count
        while i < count:
            tag = self.data[idx]
            if tag == 1:
                ln = struct.unpack('>H', self.data[idx+1:idx+3])[0]
                end = idx + 3 + ln
                val = self.data[idx+3:end].decode('utf-8', 'replace')
                newval = val
                if i in force_decide and i not in skip:
                    newval = force_decide[i]
                elif self._translatable(i):
                    newval = mapping.get(val, val)
                enc = modified_utf8(newval)
                if len(enc) > 0xFFFF:
                    enc = modified_utf8(val)
                parts.append(b'\x01' + struct.pack('>H', len(enc)) + enc)
                idx = end
            else:
                if tag in (7, 8, 16, 19, 20):
                    end = idx + 3
                elif tag == 15:
                    end = idx + 4
                elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
                    end = idx + 5
                elif tag in (5, 6):
                    end = idx + 9
                    i += 1
                else:
                    raise ValueError(f'unknown cp tag {tag}')
                parts.append(self.data[idx:end])
                idx = end
            i += 1
        new_cp = b''.join(parts)
        return self.data[:10] + new_cp + self.data[self.cp_end:]

    def to_bytes(self, mapping):
        parts = []
        i = 1
        idx = 10
        count = self.cp_count
        while i < count:
            tag = self.data[idx]
            if tag == 1:
                ln = struct.unpack('>H', self.data[idx+1:idx+3])[0]
                end = idx + 3 + ln
                val = self.data[idx+3:end].decode('utf-8', 'replace')
                newval = val
                if self._translatable(i):
                    newval = mapping.get(val, val)
                enc = modified_utf8(newval)
                if len(enc) > 0xFFFF:
                    enc = modified_utf8(val)
                parts.append(b'\x01' + struct.pack('>H', len(enc)) + enc)
                idx = end
            else:
                if tag in (7, 8, 16, 19, 20):
                    end = idx + 3
                elif tag == 15:
                    end = idx + 4
                elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
                    end = idx + 5
                elif tag in (5, 6):
                    end = idx + 9
                    i += 1
                else:
                    raise ValueError(f'unknown cp tag {tag}')
                parts.append(self.data[idx:end])
                idx = end
            i += 1
        new_cp = b''.join(parts)
        return self.data[:10] + new_cp + self.data[self.cp_end:]


def modified_utf8(s):
    """Encode a Python str using Java's Modified UTF-8."""
    out = bytearray()
    for ch in s:
        cp = ord(ch)
        if cp == 0:
            out += b'\xc0\x80'
        elif cp < 0x80:
            out.append(cp)
        elif cp < 0x800:
            out.append(0xC0 | (cp >> 6))
            out.append(0x80 | (cp & 0x3F))
        elif cp < 0x10000:
            out.append(0xE0 | (cp >> 12))
            out.append(0x80 | ((cp >> 6) & 0x3F))
            out.append(0x80 | (cp & 0x3F))
        else:
            cp -= 0x10000
            hi = 0xD800 + (cp >> 10)
            lo = 0xDC00 + (cp & 0x3FF)
            for s2 in (hi, lo):
                out.append(0xE0 | (s2 >> 12))
                out.append(0x80 | ((s2 >> 6) & 0x3F))
                out.append(0x80 | (s2 & 0x3F))
    return bytes(out)
