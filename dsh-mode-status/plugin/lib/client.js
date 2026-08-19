// ============================================================
// dsh-mode-status client bundle v4
// 梁文谷/梁文峰 时间分段模式状态点 —— 注入 DSH Web 侧栏底部
// 形式：圆点（模式色）+ 文字（模式名 + 时间），无边框无背景，GitHub 状态点风格
// 点击 → 弹出详情面板（全时段表 / 提醒 / 规则）
// 全部使用 DSW 主题变量，自动适配亮/暗主题与皮肤；折叠侧栏时只显示圆点
// 纯前端计算北京时间，每秒刷新；不依赖任何后端
// ============================================================
window.__ModuleLoader__.load({
  id: "@dsh-external/dsh-client-ui-mode-status",
  factory: (require) => {
    var module = { exports: {} };
    var exports = module.exports;
    Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });

    // ---------- 规则（与 Project\mode-status 及 skill beijing-mode 保持一致） ----------
    var SEGMENTS = [
      { start: 0, end: 540, mode: "liangwengu", label: "梁文谷", desc: "正常回复" },
      { start: 540, end: 720, mode: "liangwenfeng", label: "梁文峰", desc: "极简回复，只保留必要结论" },
      { start: 720, end: 840, mode: "liangwengu", label: "梁文谷", desc: "正常回复" },
      { start: 840, end: 1080, mode: "liangwenfeng", label: "梁文峰", desc: "极简回复，只保留必要结论" },
      { start: 1080, end: 1440, mode: "liangwengu", label: "梁文谷", desc: "正常回复" }
    ];
    var WARNINGS = [
      { start: 530, end: 540, label: "快到梁文峰时间了，建议停下。" },
      { start: 830, end: 840, label: "快到梁文峰时间了，建议停下。" }
    ];

    // ---------- CSS（全部 DSW 主题变量；无边框无背景，融入侧栏） ----------
    var CSS = [
      /* 状态点 —— 侧栏底部，无边框无背景 */
      '#ms-side-dot{display:flex;align-items:center;gap:7px;box-sizing:border-box;width:100%;padding:7px 12px;color:var(--dsw-alias-label-secondary);font:600 12px/1.3 var(--dsw-font-base-16-font-family,"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif);cursor:pointer;user-select:none;white-space:nowrap;border-radius:8px;transition:background .12s ease,color .12s ease;text-align:left}',
      '#ms-side-dot:hover{background:var(--dsw-alias-interactive-bg-hover);color:var(--dsw-alias-label-primary)}',
      '#ms-side-dot .s-dot{width:9px;height:9px;border-radius:50%;flex:none;background:var(--dsw-alias-state-success-primary);box-shadow:0 0 5px currentColor;transition:background .3s ease}',
      '#ms-side-dot[data-mode="liangwenfeng"] .s-dot{background:var(--dsw-alias-brand-primary)}',
      '#ms-side-dot[data-warning] .s-dot{background:var(--dsw-alias-state-warn-primary);animation:ms-pulse 1.6s ease-in-out infinite}',
      '#ms-side-dot .s-label{font-weight:700;color:var(--dsw-alias-label-primary)}',
      '#ms-side-dot[data-mode="liangwengu"] .s-label{color:var(--dsw-alias-state-success-primary)}',
      '#ms-side-dot[data-mode="liangwenfeng"] .s-label{color:var(--dsw-alias-brand-primary)}',
      '#ms-side-dot .s-time{font-variant-numeric:tabular-nums;font-weight:600;color:var(--dsw-alias-label-secondary)}',
      '#ms-side-dot .s-countdown{font-variant-numeric:tabular-nums;color:var(--dsw-alias-label-tertiary);font-size:11px}',
      '#ms-side-dot[data-warning] .s-time{color:var(--dsw-alias-state-warn-primary)}',
      /* 折叠（窄 rail）时只显示圆点 */
      'body[data-dsh-sidebar-collapsed] #ms-side-dot{justify-content:center;padding:7px 0}',
      'body[data-dsh-sidebar-collapsed] #ms-side-dot .s-label,body[data-dsh-sidebar-collapsed] #ms-side-dot .s-time,body[data-dsh-sidebar-collapsed] #ms-side-dot .s-countdown{display:none}',
      '@keyframes ms-pulse{0%,100%{opacity:1}50%{opacity:.5}}',
      /* 详情面板 */
      '[data-mode-status-modal]{position:fixed;inset:0;z-index:2147483001;display:flex;align-items:center;justify-content:center;font:400 13px/1.5 var(--dsw-font-base-16-font-family,"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif)}',
      '[data-mode-status-modal] .ms-mask{position:absolute;inset:0;background:var(--dsw-alias-bg-mask-3);backdrop-filter:blur(3px)}',
      '[data-mode-status-modal] .ms-panel{position:relative;width:min(560px,92vw);max-height:86vh;overflow-y:auto;background:var(--dsw-alias-bg-layer-1);border:1px solid var(--dsw-alias-border-l2);border-radius:16px;padding:20px 22px;color:var(--dsw-alias-label-primary);box-shadow:0 20px 60px var(--dsw-alias-bg-mask-3);animation:ms-pop .18s ease-out}',
      '@keyframes ms-pop{from{opacity:0;transform:scale(.96) translateY(8px)}to{opacity:1;transform:none}}',
      '[data-mode-status-modal] .ms-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}',
      '[data-mode-status-modal] .ms-title{font-size:15px;font-weight:800;color:var(--dsw-alias-label-primary)}',
      '[data-mode-status-modal] .ms-close{background:transparent;border:1px solid var(--dsw-alias-border-l2);color:var(--dsw-alias-label-secondary);border-radius:8px;width:28px;height:28px;font-size:15px;cursor:pointer;transition:all .12s ease}',
      '[data-mode-status-modal] .ms-close:hover{color:var(--dsw-alias-label-primary);border-color:var(--dsw-alias-brand-primary);background:var(--dsw-alias-interactive-bg-hover)}',
      '[data-mode-status-modal] .ms-now{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}',
      '[data-mode-status-modal] .ms-cell{background:var(--dsw-alias-bg-layer-2);border:1px solid var(--dsw-alias-border-l1);border-radius:10px;padding:10px 12px}',
      '[data-mode-status-modal] .ms-cell b{display:block;font-size:16px;color:var(--dsw-alias-label-primary);margin-top:3px;font-variant-numeric:tabular-nums}',
      '[data-mode-status-modal] .ms-cell[data-mode="liangwengu"] b{color:var(--dsw-alias-state-success-primary)}',
      '[data-mode-status-modal] .ms-cell[data-mode="liangwenfeng"] b{color:var(--dsw-alias-brand-primary)}',
      '[data-mode-status-modal] .ms-cell[data-warning] b{color:var(--dsw-alias-state-warn-primary)}',
      '[data-mode-status-modal] .ms-cell span{font-size:11px;color:var(--dsw-alias-label-secondary)}',
      '[data-mode-status-modal] .ms-sec{margin-top:14px}',
      '[data-mode-status-modal] .ms-sec h4{font-size:12px;color:var(--dsw-alias-label-secondary);font-weight:700;margin:0 0 8px;text-transform:uppercase;letter-spacing:.04em}',
      '[data-mode-status-modal] .ms-row{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:8px;border:1px solid var(--dsw-alias-border-l1);background:var(--dsw-alias-bg-layer-2);margin-bottom:6px;font-size:12.5px}',
      '[data-mode-status-modal] .ms-row.active{border-color:var(--dsw-alias-brand-primary);box-shadow:0 0 0 1px var(--dsw-alias-brand-primary)}',
      '[data-mode-status-modal] .ms-row .r-range{font-weight:700;color:var(--dsw-alias-label-primary);font-variant-numeric:tabular-nums;min-width:104px}',
      '[data-mode-status-modal] .ms-row .r-mode{font-weight:700;min-width:88px}',
      '[data-mode-status-modal] .ms-row[data-mode="liangwengu"] .r-mode{color:var(--dsw-alias-state-success-primary)}',
      '[data-mode-status-modal] .ms-row[data-mode="liangwenfeng"] .r-mode{color:var(--dsw-alias-brand-primary)}',
      '[data-mode-status-modal] .ms-row .r-desc{color:var(--dsw-alias-label-secondary)}',
      '[data-mode-status-modal] .ms-row .r-badge{margin-left:auto;font-size:10.5px;color:var(--dsw-alias-label-tertiary)}',
      '[data-mode-status-modal] .ms-row.active .r-badge{color:var(--dsw-alias-state-success-primary);font-weight:700}',
      '[data-mode-status-modal] .ms-rule{display:flex;gap:8px;padding:4px 2px;color:var(--dsw-alias-label-secondary);font-size:12.5px}',
      '[data-mode-status-modal] .ms-rule b{color:var(--dsw-alias-label-primary)}',
      '[data-mode-status-modal] .ms-rule .dot{color:var(--dsw-alias-brand-primary);flex:none}',
      '[data-mode-status-modal] .ms-foot{margin-top:14px;padding-top:10px;border-top:1px solid var(--dsw-alias-border-l1);color:var(--dsw-alias-label-tertiary);font-size:11px;text-align:center}',
      '[data-mode-status-modal] .ms-warnbox{border:1px solid var(--dsw-alias-state-warn-primary);background:var(--dsw-alias-state-warn-secondary);color:var(--dsw-alias-state-warn-primary);border-radius:10px;padding:8px 12px;margin-top:10px;font-weight:600;display:none}',
      '[data-mode-status-modal] .ms-warnbox.show{display:block}',
      '@media (max-width:640px){[data-mode-status-modal] .ms-now{grid-template-columns:1fr}}'
    ].join("");

    // ---------- 工具 ----------
    function pad(n) { return String(n).padStart(2, "0"); }
    function beijingNow() { return new Date(Date.now() + 8 * 3600 * 1000); }
    function minuteOfDay(d) { return d.getUTCHours() * 60 + d.getUTCMinutes(); }
    function fmtHMS(d) { return pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + ":" + pad(d.getUTCSeconds()); }
    function fmtHM(m) { return pad(Math.floor(m / 60)) + ":" + pad(m % 60); }
    function fmtDate(d) { return d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate()); }

    function compute() {
      var now = beijingNow();
      var mom = minuteOfDay(now);
      var secsOfDay = mom * 60 + now.getUTCSeconds();
      var current = null;
      for (var i = 0; i < SEGMENTS.length; i++) {
        if (mom >= SEGMENTS[i].start && mom < SEGMENTS[i].end) { current = SEGMENTS[i]; break; }
      }
      if (!current) current = SEGMENTS[SEGMENTS.length - 1];
      var warning = null;
      for (var j = 0; j < WARNINGS.length; j++) {
        if (mom >= WARNINGS[j].start && mom < WARNINGS[j].end) { warning = WARNINGS[j]; break; }
      }
      var nextSwitchMin = null;
      for (var k = 0; k < SEGMENTS.length; k++) {
        if (SEGMENTS[k].end > mom) { nextSwitchMin = SEGMENTS[k].end; break; }
      }
      if (nextSwitchMin === null) nextSwitchMin = 1440;
      var countdownSec = Math.max(0, nextSwitchMin * 60 - secsOfDay);
      var nextAt = new Date(now);
      nextAt.setUTCHours(Math.floor(nextSwitchMin / 60), nextSwitchMin % 60, 0, 0);
      return { now: now, current: current, warning: warning, nextSwitch: fmtHMS(nextAt), countdownSec: countdownSec };
    }

    function fmtCountdown(sec) {
      var h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
      return pad(h) + ":" + pad(m) + ":" + pad(s);
    }

    // ---------- 侧栏底部状态点 ----------
    var dotEl = null;

    function buildDot() {
      var el = document.createElement("div");
      el.id = "ms-side-dot";
      el.setAttribute("role", "button");
      el.tabIndex = 0;
      el.title = "点击查看模式详情";
      el.innerHTML = [
        '<span class="s-dot"></span>',
        '<span class="s-label">…</span>',
        '<span class="s-time">--:--:--</span>',
        '<span class="s-countdown">→ --:--:--</span>'
      ].join("");
      el.addEventListener("click", function (e) {
        e.stopPropagation();
        openPanel();
      });
      el.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openPanel(); }
      });
      return el;
    }

    function updateDot() {
      if (!dotEl || !dotEl.isConnected) return;
      var s = compute();
      var key = s.current.mode + "|" + (s.warning ? "1" : "0") + "|" + fmtHMS(s.now) + "|" + s.nextSwitch;
      if (dotEl._msKey === key) return;
      dotEl._msKey = key;
      dotEl.dataset.mode = s.current.mode;
      if (s.warning) dotEl.dataset.warning = "";
      else delete dotEl.dataset.warning;
      var label = dotEl.querySelector(".s-label");
      var time = dotEl.querySelector(".s-time");
      var cd = dotEl.querySelector(".s-countdown");
      if (label) label.textContent = s.current.label;
      if (time) time.textContent = fmtHMS(s.now);
      if (cd) cd.textContent = "→ " + s.nextSwitch;
    }

    // 挂载到侧栏底部：找到 [data-slot='sidebar.settings']（设置区），插到它前面
    function ensureDot() {
      if (dotEl && dotEl.isConnected) return true;
      var settings = document.querySelector("[data-slot='sidebar.settings']");
      var host = settings ? settings.parentElement : null;
      if (!host) return false; // 侧栏还没渲染，等 MutationObserver
      if (!dotEl) dotEl = buildDot();
      host.insertBefore(dotEl, settings);
      updateDot();
      return true;
    }

    // ---------- 详情面板 ----------
    var modalEl = null;
    function buildModal() {
      var modal = document.createElement("div");
      modal.dataset.modeStatusModal = "";
      var mask = document.createElement("div");
      mask.className = "ms-mask";
      var panel = document.createElement("div");
      panel.className = "ms-panel";

      var nowCell = function (label, id, attr) {
        return '<div class="ms-cell" id="ms-' + id + '"' + (attr || "") + '><span>' + label + "</span><b>…</b></div>";
      };
      panel.innerHTML = [
        '<div class="ms-head"><span class="ms-title">模式状态详情</span><button class="ms-close" aria-label="关闭">×</button></div>',
        '<div class="ms-now">' +
          nowCell("当前模式", "mode") +
          nowCell("北京时间", "time") +
          nowCell("距下次切换", "countdown") +
        "</div>",
        '<div class="ms-warnbox" id="ms-warnbox"></div>',
        '<div class="ms-sec"><h4>全时段时间表</h4><div id="ms-timeline"></div></div>',
        '<div class="ms-sec"><h4>规则速览</h4><div id="ms-rules"></div></div>',
        '<div class="ms-foot">数据纯前端实时计算 · 独立看板 http://127.0.0.1:25565/ · API /api/status</div>'
      ].join("");

      // 时间表
      var tl = panel.querySelector("#ms-timeline");
      for (var i = 0; i < SEGMENTS.length; i++) {
        var s = SEGMENTS[i];
        var row = document.createElement("div");
        row.className = "ms-row";
        row.dataset.mode = s.mode;
        row.dataset.start = s.start;
        row.dataset.end = s.end;
        row.innerHTML =
          '<span class="r-range">' + fmtHM(s.start) + " - " + fmtHM(s.end) + "</span>" +
          '<span class="r-mode">' + s.label + "模式</span>" +
          '<span class="r-desc">' + s.desc + "</span>" +
          '<span class="r-badge">' + (s.mode === "liangwengu" ? "正常" : "极简") + "</span>";
        tl.appendChild(row);
      }

      // 规则
      var rules = panel.querySelector("#ms-rules");
      var ruleTexts = [
        ["梁文谷模式", "00:00-09:00 · 12:00-14:00 · 18:00-24:00，正常回复"],
        ["梁文峰模式", "09:00-12:00 · 14:00-18:00，极简回复，只保留必要结论"],
        ["提醒时段", "08:50-09:00 · 13:50-14:00，回答末尾提示「⚠️ 快到梁文峰时间了，建议停下。」"],
        ["例外", "用户明确要求详细回答时，以用户要求为准"],
        ["兜底", "未提供北京时间时，默认梁文峰模式"]
      ];
      for (var r = 0; r < ruleTexts.length; r++) {
        var div = document.createElement("div");
        div.className = "ms-rule";
        div.innerHTML = '<span class="dot">•</span><span><b>' + ruleTexts[r][0] + "</b>：" + ruleTexts[r][1] + "</span>";
        rules.appendChild(div);
      }

      var close = function () { modal.remove(); modalEl = null; };
      mask.addEventListener("click", close);
      panel.querySelector(".ms-close").addEventListener("click", close);
      modal.appendChild(mask);
      modal.appendChild(panel);
      return modal;
    }

    function updateModal() {
      if (!modalEl || !modalEl.isConnected) return;
      var s = compute();
      var modeCell = modalEl.querySelector("#ms-mode");
      modeCell.dataset.mode = s.current.mode;
      modeCell.querySelector("b").textContent = s.current.label + "模式";
      var timeCell = modalEl.querySelector("#ms-time");
      timeCell.querySelector("b").textContent = fmtHMS(s.now) + "  " + fmtDate(s.now);
      var cdCell = modalEl.querySelector("#ms-countdown");
      cdCell.querySelector("b").textContent = fmtCountdown(s.countdownSec);
      var warnbox = modalEl.querySelector("#ms-warnbox");
      if (s.warning) {
        warnbox.textContent = "⚠️ " + s.warning.label;
        warnbox.classList.add("show");
      } else {
        warnbox.classList.remove("show");
      }
      var rows = modalEl.querySelectorAll(".ms-row");
      for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var inRange = Number(row.dataset.start) === s.current.start && Number(row.dataset.end) === s.current.end;
        row.classList.toggle("active", inRange);
      }
    }

    function openPanel() {
      if (modalEl && modalEl.isConnected) { modalEl.remove(); modalEl = null; }
      modalEl = buildModal();
      document.body.appendChild(modalEl);
      updateModal();
      var onKey = function (e) { if (e.key === "Escape" && modalEl) { modalEl.remove(); modalEl = null; document.removeEventListener("keydown", onKey); } };
      document.addEventListener("keydown", onKey);
      var origClose = modalEl.querySelector(".ms-close");
      origClose.addEventListener("click", function () { document.removeEventListener("keydown", onKey); });
    }

    // ---------- 插件主体 ----------
    function apply(ctx) {
      ctx.effect(function () {
        // 注入 CSS
        var tag = document.createElement("style");
        tag.dataset.plugin = "@dsh-external/dsh-client-ui-mode-status";
        tag.dataset.pluginCss = "@dsh-external/dsh-client-ui-mode-status/styles";
        tag.textContent = CSS;
        document.head.appendChild(tag);

        // 挂载状态点到侧栏底部（侧栏渲染前静默等待）
        ensureDot();

        // 轻量守护：只观察 body 直接子节点；侧栏渲染后由定时器兜底补挂
        observer = new MutationObserver(function () {
          ensureDot();
        });
        observer.observe(document.body, { childList: true, subtree: true });

        // 每秒刷新 + 兜底补挂（侧栏可能晚于插件加载渲染）
        var timer = setInterval(function () {
          ensureDot();
          updateDot();
          updateModal();
        }, 1000);

        return function () {
          clearInterval(timer);
          if (observer) observer.disconnect();
          if (dotEl) { dotEl.remove(); dotEl = null; }
          if (modalEl) { modalEl.remove(); modalEl = null; }
          if (tag.isConnected) tag.remove();
        };
      }, "ui-mode-status: sidebar dot");
    }

    exports.apply = apply;
    return module.exports;
  }
});
