package meteordevelopment.meteorclient.renderer.text;

import com.mojang.blaze3d.textures.FilterMode;
import com.mojang.blaze3d.textures.TextureFormat;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import meteordevelopment.meteorclient.renderer.MeshBuilder;
import meteordevelopment.meteorclient.renderer.Texture;
import meteordevelopment.meteorclient.utils.render.color.Color;
import org.lwjgl.BufferUtils;
import org.lwjgl.stb.STBTTFontinfo;
import org.lwjgl.stb.STBTTPackContext;
import org.lwjgl.stb.STBTTPackedchar;
import org.lwjgl.stb.STBTTPackRange;
import org.lwjgl.stb.STBTruetype;
import org.lwjgl.system.MemoryStack;

import java.nio.ByteBuffer;
import java.nio.IntBuffer;
import java.util.ArrayList;
import java.util.List;

/**
 * On-demand glyph loader / renderer. Rasterizes characters (including CJK) lazily,
 * so any font that has the glyph can render it — unlike the stock Meteor Font which
 * only packs ASCII (0x20-0x7F).
 */
public class FontFix {
    public Texture texture;
    private final int height;
    private final float scale;
    private final float ascent;
    private final Int2ObjectOpenHashMap<CharData> charMap = new Int2ObjectOpenHashMap<>();
    private static final int SIZE = 2048;

    private final ByteBuffer buffer;
    private final STBTTFontinfo fontInfo;
    private final ByteBuffer bitmap;
    private final STBTTPackContext packContext;


    public FontFix(ByteBuffer buffer, int height) {
        this.buffer = buffer;
        this.height = height;

        fontInfo = STBTTFontinfo.create();
        STBTruetype.stbtt_InitFont(fontInfo, buffer);

        bitmap = BufferUtils.createByteBuffer(SIZE * SIZE);

        packContext = STBTTPackContext.create();
        STBTruetype.stbtt_PackBegin(packContext, bitmap, SIZE, SIZE, 0, 1);

        texture = new Texture(SIZE, SIZE, TextureFormat.RED8, FilterMode.LINEAR, FilterMode.LINEAR);
        texture.upload(bitmap);

        scale = STBTruetype.stbtt_ScaleForPixelHeight(fontInfo, height);

        try (MemoryStack stack = MemoryStack.stackPush()) {
            IntBuffer ascent = stack.mallocInt(1);
            STBTruetype.stbtt_GetFontVMetrics(fontInfo, ascent, null, null);
            this.ascent = ascent.get(0);
        }

        preloadAsciiCharacters();
    }

    private void preloadAsciiCharacters() {
        STBTTPackedchar.Buffer cdata = STBTTPackedchar.create(128);
        STBTTPackRange.Buffer packRange = STBTTPackRange.create(1);
        packRange.put(STBTTPackRange.create().set(height, 32, null, 128, cdata, (byte) 2, (byte) 2));
        packRange.flip();
        STBTruetype.stbtt_PackFontRanges(packContext, buffer, 0, packRange);
        for (int i = 0; i < cdata.capacity(); i++) {
            putCharData(i + 32, cdata.get(i));
        }
        createTexture();
    }

    private void loadCharacters(List<Integer> codePoints) {
        // Load ALL missing glyphs in one batch so text appears immediately instead of
        // popping in over many frames (which stuttered). One texture re-upload per
        // screen is far cheaper than dozens of partial uploads.
        for (Integer codePoint : codePoints) {
            loadCharacter(codePoint);
        }
        createTexture();
    }

    private void loadCharacter(int codePoint) {
        if (charMap.containsKey(codePoint)) return;
        STBTTPackedchar.Buffer cdata = STBTTPackedchar.create(1);
        STBTTPackRange.Buffer packRange = STBTTPackRange.create(1);
        packRange.put(STBTTPackRange.create().set(height, codePoint, null, 1, cdata, (byte) 2, (byte) 2));
        packRange.flip();
        STBTruetype.stbtt_PackFontRanges(packContext, buffer, 0, packRange);
        putCharData(codePoint, cdata.get(0));
    }

    private void putCharData(int codePoint, STBTTPackedchar packedChar) {
        float ipw = 1f / SIZE;
        float iph = 1f / SIZE;
        charMap.put(codePoint, new CharData(
            packedChar.xoff(),
            packedChar.yoff(),
            packedChar.xoff2(),
            packedChar.yoff2(),
            packedChar.x0() * ipw,
            packedChar.y0() * iph,
            packedChar.x1() * ipw,
            packedChar.y1() * iph,
            packedChar.xadvance()
        ));
    }

    private void createTexture() {
        texture = new Texture(SIZE, SIZE, TextureFormat.RED8, FilterMode.LINEAR, FilterMode.LINEAR);
        texture.upload(bitmap);
    }

    public double getWidth(String string, int length) {
        double width = 0;
        if (tryLoadString(string)) return width;
        for (int i = 0; i < length; i++) {
            int cp = string.charAt(i);
            CharData c = charMap.get(cp);
            if (c == null) continue;
            width += c.xAdvance;
        }
        return width;
    }

    public int getHeight() {
        return height;
    }

    private boolean tryLoadString(String s) {
        List<Integer> charPoints = null;
        for (int i = 0; i < s.length(); i++) {
            int cp = s.charAt(i);
            CharData c = charMap.get(cp);
            if (c == null) {
                if (charPoints == null) charPoints = new ArrayList<>();
                charPoints.add(cp);
            }
        }
        if (charPoints != null) {
            loadCharacters(charPoints);
            return true;
        }
        return false;
    }

    public double render(MeshBuilder mesh, String string, double x, double y, Color color, double scale) {
        if (tryLoadString(string)) return x;
        y += ascent * this.scale * scale;

        int length = string.length();
        mesh.ensureCapacity(length * 4, length * 6);
        for (int i = 0; i < length; i++) {
            int cp = string.charAt(i);
            CharData c = charMap.get(cp);
            if (c == null) continue;
            mesh.quad(
                mesh.vec2(x + c.x0 * scale, y + c.y0 * scale).vec2(c.u0, c.v0).color(color).next(),
                mesh.vec2(x + c.x0 * scale, y + c.y1 * scale).vec2(c.u0, c.v1).color(color).next(),
                mesh.vec2(x + c.x1 * scale, y + c.y1 * scale).vec2(c.u1, c.v1).color(color).next(),
                mesh.vec2(x + c.x1 * scale, y + c.y0 * scale).vec2(c.u1, c.v0).color(color).next()
            );
            x += c.xAdvance * scale;
        }
        return x;
    }

    private record CharData(float x0, float y0, float x1, float y1, float u0, float v0, float u1, float v1, float xAdvance) {}
}
