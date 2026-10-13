/* WiFi 密码查看器 —— 前端逻辑
 * 数据来自 pywebview API：window.pywebview.api.scan() / qr_matrix(ssid, password)
 * 交互约定（评审 round-1）：已连接置顶并默认选中；一键显隐 + Esc；复制提示不带明文；
 * 键盘流 / ↑↓ Enter C；二维码可扫。
 */
"use strict";

const state = {
  networks: [],
  selected: 0,
  query: "",
  shown: new Set(),
  loading: true,
  error: null,
  note: null,           // 连接状态不可用等降级说明
  connectedAvailable: false,
};

/* ── 工具 ────────────────────────────────────────────── */
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const mask = (pw) => "•".repeat(Math.min(pw.length, 14));

function toast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove("show"), 1600);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch { /* 忽略：剪贴板不可用 */ }
    ta.remove();
  }
  toast("密码已复制到剪贴板");
}

function visibleNetworks() {
  const q = state.query.trim().toLowerCase();
  return state.networks.filter((n) => !q || n.ssid.toLowerCase().includes(q));
}

/* ── 数据加载 ────────────────────────────────────────── */
async function load() {
  state.loading = true;
  state.error = null;
  render();
  try {
    const result = await window.pywebview.api.scan();
    if (!result || result.ok !== true) throw new Error((result && result.error) || "未知错误");
    // 已连接置顶（稳定排序，其余保持 netsh 原序）
    state.networks = result.networks.slice().sort((a, b) => (b.connected ? 1 : 0) - (a.connected ? 1 : 0));
    state.connectedAvailable = !!result.connected_available;
    state.note = result.note || null;
    state.shown.clear();
    const connectedIdx = state.networks.findIndex((n) => n.connected);
    state.selected = connectedIdx >= 0 ? connectedIdx : 0;
  } catch (e) {
    state.error = String((e && e.message) || e);
    state.networks = [];
  } finally {
    state.loading = false;
    render();
  }
}

/* ── 渲染 ────────────────────────────────────────────── */
function render() {
  renderSidebar();
  renderDetail();
  renderFootNote();
}

function renderSidebar() {
  const list = visibleNetworks();
  if (state.loading) {
    $("count-line").textContent = "正在读取本机 WiFi 存档…";
    $("list").innerHTML = '<div class="list-empty">正在读取…</div>';
    $("toggle-all").disabled = true;
    return;
  }
  if (state.error) {
    $("count-line").textContent = "读取失败";
    $("list").innerHTML = '<div class="list-empty">读取失败</div>';
    $("toggle-all").disabled = true;
    return;
  }
  $("count-line").textContent = `已保存 ${state.networks.length} 个网络${state.connectedAvailable ? "" : " · 未取得连接状态"}`;

  const allShown = list.length > 0 && list.every((n) => state.shown.has(n.ssid));
  const btn = $("toggle-all");
  btn.disabled = list.length === 0;
  btn.textContent = allShown ? "全部隐藏" : "全部显示";

  if (list.length === 0) {
    $("list").innerHTML = state.networks.length === 0
      ? '<div class="list-empty">这台电脑还没有保存过任何 WiFi<br>先连接一个网络再回来看看</div>'
      : `<div class="list-empty">没有找到匹配的网络<br><button class="mini" onclick="clearSearch()">清除搜索</button></div>`;
    return;
  }

  if (state.selected >= list.length) state.selected = 0;
  $("list").innerHTML = list.map((n, i) => `
    <div class="row ${i === state.selected ? "sel" : ""}" data-idx="${i}">
      <div class="ico">${n.note && !n.has_password && /开放/.test(n.note) ? "🔓" : "🔒"}</div>
      <div class="meta">
        <div class="ssid">${esc(n.ssid)}</div>
        <div class="sub">${esc(n.authentication || "未知加密")}${n.cipher ? " · " + esc(n.cipher) : ""}</div>
      </div>
      ${n.connected ? '<span class="conn">已连接</span>' : ""}
    </div>`).join("");
  document.querySelectorAll(".row").forEach((row) =>
    row.addEventListener("click", () => selectIndex(Number(row.dataset.idx))));
}

function renderDetail() {
  const el = $("detail");
  if (state.loading) {
    el.innerHTML = '<div class="placeholder">正在读取本机 WiFi 存档…</div>';
    return;
  }
  if (state.error) {
    el.innerHTML = `
      <div class="err-card">
        <h3>读取失败</h3>
        <p>${esc(state.error)}</p>
        <p style="margin-top:8px">小提示：若 Windows 的“无线局域网服务 (WlanSvc)”未运行，请先启动该服务后重试。</p>
        <button class="btn primary" onclick="load()">重试</button>
      </div>`;
    return;
  }
  const list = visibleNetworks();
  const cur = list[state.selected];
  if (!cur) {
    el.innerHTML = state.networks.length === 0
      ? '<div class="placeholder">这台电脑还没有保存过任何 WiFi<br>先在系统里连接一个网络，再点击左上角 ↻ 刷新</div>'
      : '<div class="placeholder">左侧选择一个网络查看详情</div>';
    return;
  }

  const shownPw = state.shown.has(cur.ssid);
  let pwBox;
  if (cur.has_password) {
    pwBox = `
      <div class="pw-box">
        <button class="pw-eye" id="pw-eye" title="${shownPw ? "隐藏" : "显示"}密码">${shownPw ? "🙈" : "👁"}</button>
        <div class="pw-val ${shownPw ? "shown" : ""}" id="pw-val">${shownPw ? esc(cur.password) : mask(cur.password)}</div>
        <button class="btn primary" id="copy-btn">复制密码</button>
        <button class="btn secondary" id="qr-btn">二维码</button>
      </div>`;
  } else {
    pwBox = `
      <div class="pw-box">
        <div class="pw-note">${esc(cur.note || "该网络没有保存密码")}</div>
        <button class="btn" disabled>复制密码</button>
      </div>`;
  }

  const kvRows = [
    ["加密类型", cur.authentication || "未知"],
    ...(cur.cipher ? [["加密算法", cur.cipher]] : []),
    ["连接状态", cur.connected ? "已连接" : "未连接（或状态不可用）"],
  ];

  el.innerHTML = `
    <h2>${esc(cur.ssid)}</h2>
    <div class="subrow">
      <span class="tag ok">🔒 ${esc(cur.authentication || "未知加密")}</span>
      ${cur.connected ? '<span class="tag blue">已连接</span>' : '<span class="tag">未连接</span>'}
    </div>
    <div class="panel">
      <div class="t">网络密码</div>
      ${pwBox}
    </div>
    <div class="panel">
      <div class="t">网络详情</div>
      <div class="kv">
        ${kvRows.map(([k, v]) => `<div class="r"><span class="k">${esc(k)}</span><span class="v">${esc(v)}</span></div>`).join("")}
      </div>
    </div>`;

  if (cur.has_password) {
    $("pw-eye").addEventListener("click", () => toggleShow(cur.ssid));
    $("copy-btn").addEventListener("click", () => copyText(cur.password));
    $("qr-btn").addEventListener("click", () => openQR(cur));
  }
}

function renderFootNote() {
  const el = $("foot-note");
  if (state.note) {
    el.textContent = state.note;
    el.classList.add("warn");
  } else {
    el.textContent = "密码读取自本机存档 · 不联网 · 不上传";
    el.classList.remove("warn");
  }
}

/* ── 交互 ────────────────────────────────────────────── */
function selectIndex(i) {
  state.selected = i;
  render();
}

function toggleShow(ssid) {
  if (state.shown.has(ssid)) state.shown.delete(ssid);
  else state.shown.add(ssid);
  render();
}

function toggleAll() {
  const list = visibleNetworks();
  const all = list.length > 0 && list.every((n) => state.shown.has(n.ssid));
  list.forEach((n) => { if (n.has_password) { if (all) state.shown.delete(n.ssid); else state.shown.add(n.ssid); } });
  render();
}

function clearSearch() {
  state.query = "";
  $("search").value = "";
  render();
}

/* 二维码弹窗 */
async function openQR(net) {
  try {
    const matrix = await window.pywebview.api.qr_matrix(net.ssid, net.password);
    const canvas = $("qr-canvas");
    const quiet = 4; // 静默区
    const size = matrix.length + quiet * 2;
    const cell = Math.max(1, Math.floor(canvas.width / size));
    const offset = Math.floor((canvas.width - cell * size) / 2);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#111827";
    matrix.forEach((row, y) => row.forEach((on, x) => {
      if (on) ctx.fillRect(offset + (x + quiet) * cell, offset + (y + quiet) * cell, cell, cell);
    }));
    $("qr-ssid").textContent = net.ssid;
    $("qr-pw").textContent = net.password;
    $("qr-modal").classList.remove("hidden");
  } catch (e) {
    toast("二维码生成失败");
  }
}
function closeQR() { $("qr-modal").classList.add("hidden"); }
const qrOpen = () => !$("qr-modal").classList.contains("hidden");

/* ── 键盘流（评审 round-1） ──────────────────────────── */
document.addEventListener("keydown", (e) => {
  const t = e.target;
  const typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);

  if (qrOpen()) {
    if (e.key === "Escape") closeQR();
    return;
  }
  if (typing) {
    if (e.key === "Escape" && t.id === "search") clearSearch();
    return;
  }
  if (e.key === "Escape") {           // 全部隐藏，防投屏/截屏泄漏
    state.shown.clear();
    render();
    return;
  }
  const list = visibleNetworks();
  if (e.key === "ArrowDown") { state.selected = Math.min(state.selected + 1, list.length - 1); render(); e.preventDefault(); }
  else if (e.key === "ArrowUp") { state.selected = Math.max(state.selected - 1, 0); render(); e.preventDefault(); }
  else if (e.key === "Enter" && list[state.selected]) { toggleShow(list[state.selected].ssid); e.preventDefault(); }
  else if ((e.key === "c" || e.key === "C") && list[state.selected] && list[state.selected].has_password) {
    copyText(list[state.selected].password);
    e.preventDefault();
  }
  else if (e.key === "/") { $("search").focus(); e.preventDefault(); }
});

/* ── 绑定与启动 ──────────────────────────────────────── */
$("refresh").addEventListener("click", load);
$("toggle-all").addEventListener("click", toggleAll);
$("qr-close").addEventListener("click", closeQR);
$("qr-backdrop").addEventListener("click", closeQR);
$("search").addEventListener("input", (e) => {
  state.query = e.target.value;
  const pos = e.target.selectionStart;
  render();
  const s = $("search");
  if (s) { s.focus(); try { s.setSelectionRange(pos, pos); } catch { /* 忽略 */ } }
});

if (window.pywebview && window.pywebview.api) {
  load();
} else {
  window.addEventListener("pywebviewready", load);
  setTimeout(() => {
    if (state.loading && !state.error && state.networks.length === 0 && !window.pywebview) {
      state.loading = false;
      state.error = "未检测到应用后端：请通过 run.bat（或 py wifi_pass_viewer/app.py）启动，而不是直接用浏览器打开本文件。";
      render();
    }
  }, 1500);
}
