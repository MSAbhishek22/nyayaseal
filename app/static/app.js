/* NyayaSeal — front-end logic. No external assets.
   Every control does a real thing; every result comes from the server. */
"use strict";
const esc = s => String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const $ = id => document.getElementById(id);
const shortHash = h => h ? h.slice(0,12) + "…" : "";
let SELECTED = null;
let LAST_SEAL = null; /* last seal result, for the receipt download */

/* Copy helper: every hash/blob id gets a COPY button (constitution §8). */
async function copyText(text, btn){
  try { await navigator.clipboard.writeText(text); }
  catch (e) {
    const ta = document.createElement("textarea");
    ta.value = text; document.body.appendChild(ta); ta.select();
    document.execCommand("copy"); ta.remove();
  }
  if (btn) { const old = btn.textContent; btn.textContent = "COPIED ✓";
    setTimeout(() => { btn.textContent = old; }, 1500); }
}
document.addEventListener("click", e => {
  const btn = e.target.closest("[data-copy]");
  if (btn) copyText(btn.getAttribute("data-copy"), btn);
});
function copyBtn(value){
  return `<button type="button" class="copy-btn" data-copy="${esc(value)}">COPY</button>`;
}

/* ---------- motion: toggle + reveal + 3D support ---------- */
const root = document.documentElement;
const toggle = $("motion-toggle");
function setLowMotion(low){
  root.setAttribute("data-motion", low ? "low" : "full");
  toggle.setAttribute("aria-pressed", String(low));
  toggle.textContent = "Low motion: " + (low ? "on" : "off");
  applyVaultTransform();
}
toggle.addEventListener("click", () => setLowMotion(root.getAttribute("data-motion") !== "low"));
if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) setLowMotion(true);

const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}), {threshold:.1});
document.querySelectorAll(".rv").forEach(el => io.observe(el));

/* 3D support probe: if transforms are unsupported, fall back to a flat grid. */
const supports3d = (() => {
  const el = document.createElement("div");
  return "transform" in el.style && "perspective" in el.style;
})();
if (!supports3d) document.body.classList.add("no3d");

/* ---------- api ---------- */
async function api(path, body){
  const res = await fetch(path, body ? {method:"POST",
    headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)} : {});
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || ("Request failed: " + res.status));
  return data;
}
async function postFile(path, file, fields){
  const fd = new FormData();
  if (file) fd.append("file", file);
  Object.entries(fields || {}).forEach(([k,v]) => fd.append(k, v));
  const res = await fetch(path, {method:"POST", body: fd});
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || ("Request failed: " + res.status));
  return data;
}

/* ---------- drop zones ---------- */
function wireDropzone(zoneId, inputId, nameId){
  const zone = $(zoneId), input = $(inputId);
  zone.addEventListener("click", e => { if (e.target !== input) input.click(); });
  zone.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }
  });
  ["dragover","dragenter"].forEach(ev => zone.addEventListener(ev, e => {
    e.preventDefault(); zone.classList.add("over");
  }));
  ["dragleave","drop"].forEach(ev => zone.addEventListener(ev, e => {
    e.preventDefault(); zone.classList.remove("over");
  }));
  zone.addEventListener("drop", e => {
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) { input.files = e.dataTransfer.files; showFileName(nameId, f); }
  });
  input.addEventListener("change", () => showFileName(nameId, input.files[0]));
}
function showFileName(id, f){
  $(id).textContent = f ? ("Selected: " + f.name + " (" + f.size.toLocaleString() + " bytes)") : "";
}
wireDropzone("dropzone","seal-file","seal-file-name");
wireDropzone("verify-dropzone","verify-file","verify-file-name");

/* ---------- seal ---------- */
$("seal-btn").addEventListener("click", async () => {
  const out = $("seal-out");
  const file = $("seal-file").files[0];
  const text = $("seal-text").value;
  const fields = {title: $("seal-title").value, doc_type: $("seal-type").value,
                  issuer: $("seal-issuer").value};
  out.innerHTML = "<p class='hint'>Sealing…</p>";
  try {
    let r;
    if (file) r = await postFile("/api/seal", file, fields);
    else r = await api("/api/seal", {...fields, text});
    const d = r.document;
    LAST_SEAL = r;
    out.innerHTML = `<div class="okbox"><strong>${r.duplicate ? "Already sealed — identical bytes." : "Sealed."}</strong><br>
      <strong>${esc(d.title)}</strong> · ${esc(d.doc_type)} · issuer ${esc(d.issuer)}<br>
      Blob id <span class="mono">${esc(d.blob_id)}</span>${copyBtn(d.blob_id)}<br>
      Receipt <span class="mono">${esc(r.receipt.receipt_id)}</span> · sealed ${esc(d.timestamp_utc)}</div>
      <button class="btn secondary" id="receipt-dl" type="button">Download receipt (.json)</button>`;
    $("receipt-dl").addEventListener("click", () => {
      const blob = new Blob([JSON.stringify(LAST_SEAL, null, 2)], {type:"application/json"});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "nyayaseal-receipt-" + d.blob_id.slice(0,12) + ".json";
      a.click(); URL.revokeObjectURL(a.href);
    });
    SELECTED = d.blob_id;
    refreshAll();
  } catch (err) {
    out.innerHTML = `<div class="err"><strong>Not sealed.</strong> ${esc(err.message)}</div>`;
  }
});
$("seal-clear").addEventListener("click", () => {
  ["seal-file","seal-text","seal-title","seal-issuer"].forEach(id => { $(id).value = ""; });
  $("seal-file-name").textContent = ""; $("seal-out").innerHTML = "";
});

/* ---------- verify ---------- */
$("verify-btn").addEventListener("click", async () => {
  const out = $("verify-out");
  const file = $("verify-file").files[0];
  const hash = $("verify-hash").value.trim();
  if (!file && !hash) {
    out.innerHTML = `<div class="err">Nothing to verify — upload a file or paste a blob id first.</div>`;
    return;
  }
  out.innerHTML = "<p class='hint'>Verifying — re-hashing and comparing…</p>";
  try {
    let r;
    if (file) r = await postFile("/api/verify", file, hash ? {expected_blob_id: hash} : {});
    else r = await api("/api/verify", {hash});
    renderVerdict(out, r);
    refreshAll();
  } catch (err) {
    out.innerHTML = `<div class="err"><strong>Verification failed.</strong> ${esc(err.message)}</div>`;
  }
});
$("verify-clear").addEventListener("click", () => {
  $("verify-file").value = ""; $("verify-hash").value = "";
  $("verify-file-name").textContent = "";
  $("verify-out").innerHTML = "<p class='hint'>Cleared. Upload a file or paste a hash and press “Verify now”.</p>";
});
function renderVerdict(out, r){
  const cls = r.verdict === "AUTHENTIC" ? "AUTHENTIC" : "NOTFOUND";
  const d = r.document;
  out.innerHTML = `
    <p><span class="verdict ${cls}">${esc(r.verdict)}</span></p>
    <p>${esc(r.explanation || "")}</p>
    <p>Computed hash<br><span class="mono">${esc(r.computed_hash || "")}</span>${r.computed_hash ? copyBtn(r.computed_hash) : ""}</p>
    ${d ? `<p><strong>${esc(d.title)}</strong><br>${esc(d.doc_type)} · issuer ${esc(d.issuer)} ·
      sealed ${esc(d.timestamp_utc)}<br>Blob id <span class="mono">${esc(d.blob_id)}</span>${copyBtn(d.blob_id)}</p>` : ""}
    <p class="hint">Verification proves the bytes are unchanged — not that the content is legally true.
    General legal information, not legal advice.</p>
    <p class="hint">Receipt <span class="mono">${esc(r.receipt ? r.receipt.receipt_id : "")}</span> ·
    backend <span class="mono">${esc(r.backend || "local-vault")}</span></p>`;
}

/* ---------- tamper demo ---------- */
$("tamper-btn").addEventListener("click", async () => {
  const out = $("tamper-out");
  const id = $("tamper-select").value;
  if (!id) { out.innerHTML = `<div class="err">Pick a sealed document first.</div>`; return; }
  out.innerHTML = "<p class='hint'>Flipping one character and re-checking…</p>";
  try {
    const r = await api("/api/tamper-demo", {blob_id: id});
    out.innerHTML = `<div class="warnbox"><strong class="verdict TAMPERED">TAMPERED</strong><br>
      ${esc(r.explanation)}<br>
      Original blob id <span class="mono">${esc(r.original_blob_id)}</span><br>
      Tampered copy's hash <span class="mono">${esc(r.tampered_hash)}</span><br>
      <span class="hint">Receipt <span class="mono">${esc(r.receipt.receipt_id)}</span> ·
      backend <span class="mono">${esc(r.backend)}</span></span></div>`;
    refreshAll();
  } catch (err) {
    out.innerHTML = `<div class="err"><strong>Demo failed.</strong> ${esc(err.message)}</div>`;
  }
});

/* ---------- register + 3D vault ---------- */
let rotY = -18, rotX = 8;
function applyVaultTransform(){
  const stage = $("vault-stage");
  if (!stage) return;
  const low = root.getAttribute("data-motion") === "low" || !supports3d;
  stage.style.transform = low ? "none" : `rotateX(${rotX}deg) rotateY(${rotY}deg)`;
}
$("rot-left").addEventListener("click", () => { rotY -= 30; applyVaultTransform(); });
$("rot-right").addEventListener("click", () => { rotY += 30; applyVaultTransform(); });
$("rot-reset").addEventListener("click", () => { rotY = -18; rotX = 8; applyVaultTransform(); });
(function dragRotate(){
  const scene = $("vault-scene");
  let dragging = false, lastX = 0, lastY = 0;
  scene.addEventListener("pointerdown", e => {
    if (root.getAttribute("data-motion") === "low") return;
    dragging = true; lastX = e.clientX; lastY = e.clientY;
    scene.setPointerCapture(e.pointerId);
  });
  scene.addEventListener("pointermove", e => {
    if (!dragging) return;
    rotY += (e.clientX - lastX) * 0.4;
    rotX = Math.max(-30, Math.min(30, rotX - (e.clientY - lastY) * 0.3));
    lastX = e.clientX; lastY = e.clientY;
    applyVaultTransform();
  });
  ["pointerup","pointercancel"].forEach(ev => scene.addEventListener(ev, () => { dragging = false; }));
})();

function renderRegister(docs){
  const tb = $("register-body");
  if (!docs.length) {
    tb.innerHTML = "<tr><td colspan='5'>No documents sealed yet — seal the first one in §01.</td></tr>";
  } else {
    tb.innerHTML = docs.map(d =>
      `<tr data-id="${esc(d.blob_id)}" class="${d.blob_id===SELECTED?"selected":""}">
        <td><strong>${esc(d.title)}</strong></td><td>${esc(d.doc_type)}</td>
        <td>${esc(d.issuer)}</td><td class="mono">${esc(String(d.timestamp_utc).slice(0,19))}Z</td>
        <td class="mono">${esc(shortHash(d.blob_id))}</td></tr>`).join("");
    tb.querySelectorAll("tr[data-id]").forEach(tr => tr.addEventListener("click", () => {
      SELECTED = tr.dataset.id; renderRegister(docs); renderDetail();
    }));
  }
  // 3D cards: one real card per sealed doc, fanned in depth.
  const stage = $("vault-stage");
  if (!docs.length) {
    stage.innerHTML = "<p class='muted' style='padding:20px'>No sealed documents yet.</p>";
  } else {
    stage.innerHTML = docs.slice(0,8).map((d,i) => {
      const z = supports3d ? (i * -46) : 0;
      const y = supports3d ? (i * -8) : 0;
      return `<article class="vault-card" tabindex="0" role="button" data-id="${esc(d.blob_id)}"
        aria-label="Document ${esc(d.title)}, sealed ${esc(String(d.timestamp_utc).slice(0,10))}, verdict authentic"
        style="transform:translateZ(${z}px) translateY(${y}px)">
        <span class="pill sealed">SEALED</span>
        <h3>${esc(d.title)}</h3>
        <p class="muted" style="margin:0;font-size:.85rem">${esc(d.doc_type)} · ${esc(d.issuer)}</p>
        <p class="mono" style="margin:0">${esc(shortHash(d.blob_id))}</p>
        <span class="seal-stamp">✓ HASH-SEALED</span></article>`;
    }).join("");
    stage.querySelectorAll(".vault-card[data-id]").forEach(card => {
      const pick = () => { SELECTED = card.dataset.id; renderRegister(docs); renderDetail();
        document.getElementById("vault").scrollIntoView({behavior:"smooth"}); };
      card.addEventListener("click", pick);
      card.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); }
        if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
          e.preventDefault();
          const cards = [...stage.querySelectorAll(".vault-card")];
          const i = cards.indexOf(card);
          const next = cards[(i + (e.key === "ArrowRight" ? 1 : -1) + cards.length) % cards.length];
          if (next) next.focus();
        }
      });
    });
  }
  applyVaultTransform();
  // tamper-demo picker
  const sel = $("tamper-select");
  const prev = sel.value;
  sel.innerHTML = docs.map(d =>
    `<option value="${esc(d.blob_id)}">${esc(d.title)}</option>`).join("");
  if (docs.some(d => d.blob_id === prev)) sel.value = prev;
}

async function renderDetail(){
  const out = $("detail-out");
  if (!SELECTED) { out.innerHTML = ""; return; }
  const d = await api("/api/doc?id=" + encodeURIComponent(SELECTED));
  if (!d.ok) { out.innerHTML = `<div class="err">${esc(d.error || "Not found.")}</div>`; return; }
  const doc = d.document;
  out.innerHTML = `<div class="card"><h3>${esc(doc.title)}</h3>
    <p><span class="pill sealed">SEALED</span> ${esc(doc.doc_type)} · issuer ${esc(doc.issuer)} ·
    sealed ${esc(doc.timestamp_utc)}</p>
    <p>Blob id (SHA-256)<br><span class="mono">${esc(doc.blob_id)}</span>${copyBtn(doc.blob_id)}</p>
    <p class="hint">${esc(doc.size_bytes)} bytes · stored at data/blobs/${esc(doc.blob_id.slice(0,12))}… ·
    backend <span class="mono">${esc(doc.backend)}</span></p>
    <button class="btn secondary" id="detail-verify" type="button">Verify this blob id</button></div>`;
  $("detail-verify").addEventListener("click", () => {
    $("verify-hash").value = doc.blob_id;
    document.getElementById("verify").scrollIntoView({behavior:"smooth"});
    $("verify-btn").click();
  });
}

/* ---------- audit ---------- */
$("verify-chain").addEventListener("click", async () => {
  try {
    const r = await api("/api/audit/verify");
    $("chain-out").textContent = r.ok
      ? `Chain OK — ${r.checked} receipt(s) re-hashed, no break.`
      : `Chain BROKEN at seq ${r.bad_at} (checked ${r.checked}).`;
  } catch (err) {
    $("chain-out").textContent = "Could not verify the chain — server unreachable. Try again.";
  }
});
function renderAudit(entries){
  const ul = $("audit-list");
  if (!entries.length) { ul.innerHTML = "<li>No receipts yet.</li>"; return; }
  ul.innerHTML = entries.slice(-12).reverse().map(e =>
    `<li><strong>${esc(e.receipt_id)}</strong> · ${esc(String(e.timestamp_utc).slice(0,19))}Z<br>
     ${esc(e.action)} — <span class="mono">${esc(shortHash(e.blob_id))}</span><br>
     <span class="muted">${esc(e.detail)}</span><br>
     hash <span class="mono">${esc(String(e.hash).slice(0,16))}…</span> ·
     prev <span class="mono">${esc(String(e.prev_hash).slice(0,16))}…</span></li>`).join("");
}

/* ---------- refresh ---------- */
async function refreshAll(){
  try {
    const [st, docs, audit] = await Promise.all([
      api("/api/status"), api("/api/docs"), api("/api/audit")]);
    $("backend-badge").textContent = "[local-vault] — Walrus testnet not connected";
    $("backend-badge").title = st.walrus_blocker || "";
    $("footer-backend").textContent = st.backend;
    $("walrus-note-text").textContent = st.walrus_blocker || "";
    renderRegister(docs.documents || []);
    renderAudit(audit.entries || []);
    const verifies = (audit.entries || []).filter(e => e.action === "verify").length;
    $("stat-docs").textContent = (docs.documents || []).length;
    $("stat-verifies").textContent = verifies;
    $("stat-chain").textContent = (audit.entries || []).length + " receipts";
    if (SELECTED) renderDetail();
  } catch (err) {
    $("backend-badge").textContent = "server unreachable";
    $("register-body").innerHTML = `<tr><td colspan="5">Could not reach the server: ${esc(err.message)}</td></tr>`;
  }
}
/* Deep link: ?blob=<id> pre-fills Verify and runs the check (constitution §7). */
async function deepLink(){
  const blob = new URLSearchParams(location.search).get("blob");
  if (!blob) return;
  $("verify-hash").value = blob;
  document.getElementById("verify").scrollIntoView();
  $("verify-btn").click();
}
refreshAll().then(deepLink);
