/* Shared storefront logic: fetch() + low-DOM rendering. No business logic in HTML. */
const API = "/api";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

async function api(path, timeoutMs = 30000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch(API + path, { signal: ctrl.signal });
    if (!r.ok) throw new Error(`API ${r.status}`);
    return await r.json();
  } catch (e) {
    if (e.name === "AbortError") throw new Error("Request timed out. Please refresh.");
    throw e;
  } finally {
    clearTimeout(t);
  }
}

async function apiPost(path, body) {
  const r = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) {
    const err = new Error(d.error || `API ${r.status}`);
    err.status = r.status;  // e.g. 409 for price-change conflicts
    err.data = d;           // full response body (changes[], cart, …)
    throw err;
  }
  return d;
}

/* Cart: badge count + add helper shared by product/listing pages */
async function refreshCartCount() {
  try {
    const d = await api("/cart/");
    const el = $("#cart-count");
    if (el) { el.textContent = d.item_count; el.style.display = d.item_count ? "" : "none"; }
  } catch (e) { /* cart unavailable — ignore */ }
}

async function addToCart(variantId, qty) {
  const d = await apiPost("/cart/add/", { variant_id: variantId, quantity: qty || 1 });
  await refreshCartCount();
  return d;
}

async function quickAddBySlug(slug) {
  const p = await api(`/products/${slug}/`);
  const v = (p.variants || []).find((x) => x.is_active) || p.variants[0];
  if (!v) throw new Error("No variant available");
  return addToCart(v.id, 1);
}

const inr = (n) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });

function stars(r) {
  const n = Math.round(Number(r));
  return "★".repeat(n) + "☆".repeat(5 - n);
}

function productCard(p) {
  const img = p.primary_image || "https://picsum.photos/seed/na/400/400";
  const off = p.discount_pct > 0 ? `<span class="off">${Number(p.discount_pct)}% off</span>` : "";
  return `<div class="card">
    <a href="/product/${p.slug}/"><img loading="lazy" src="${img}" alt="${esc(p.name)}"></a>
    <div class="body">
      <div class="brand">${esc(p.brand_name || "")}</div>
      <a href="/product/${p.slug}/"><div class="name">${esc(p.name)}</div></a>
      <div><span class="price">${inr(p.final_price)}</span>
        ${p.discount_pct > 0 ? `<span class="mrp">${inr(p.price)}</span>${off}` : ""}</div>
      <div class="rating">${stars(p.rating)} ${p.rating} (${p.review_count})</div>
      <button class="btn primary btn-quick-add" data-slug="${p.slug}">Add to cart</button>
    </div>
  </div>`;
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function pager(total, page, pageSize, onGo) {
  const pages = Math.ceil(total / pageSize);
  if (pages <= 1) return "";
  let h = `<div class="pager">`;
  const btn = (p, label, cls = "") => `<button class="${cls}" data-p="${p}">${label}</button>`;
  if (page > 1) h += btn(page - 1, "← Prev");
  for (let p = Math.max(1, page - 2); p <= Math.min(pages, page + 2); p++)
    h += btn(p, p, p === page ? "active" : "");
  if (page < pages) h += btn(page + 1, "Next →");
  return h + `</div>`;
}

function bindPager(container, onGo) {
  $$("button[data-p]", container).forEach((b) =>
    b.addEventListener("click", () => onGo(Number(b.dataset.p)))
  );
}

// Header search wiring (present on every page)
document.addEventListener("DOMContentLoaded", () => {
  refreshCartCount();
  // Quick-add buttons on product cards (delegated — cards render dynamically)
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".btn-quick-add");
    if (!btn) return;
    e.preventDefault();
    if (btn.disabled) return;
    btn.disabled = true;
    const orig = btn.textContent;
    try { await quickAddBySlug(btn.dataset.slug); btn.textContent = "✓ Added!"; }
    catch (err) { alert(err.message); btn.textContent = orig; }
    setTimeout(() => { btn.disabled = false; btn.textContent = "Add to cart"; }, 1200);
  });
  const form = $("#search-form");
  if (form) form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = $("#search-input").value.trim();
    if (q) location.href = "/search/?q=" + encodeURIComponent(q);
  });
});

/* Auth: navbar state driven by /api/accounts/me/ (single source of truth) */
let __currentUser = null;
async function refreshAuthNav() {
  const el = $("#auth-nav");
  if (!el) return;
  try {
    const d = await api("/accounts/me/");
    __currentUser = d.user;
    if (d.user) {
      el.innerHTML = `<a href="/my-orders/">Hi, ${esc(d.user.name.split(" ")[0])}</a>
        <a href="#" id="logout-link">Logout</a>`;
      $("#logout-link").addEventListener("click", async (e) => {
        e.preventDefault();
        await apiPost("/accounts/logout/", {});
        __currentUser = null;
        await refreshAuthNav();
        await refreshCartCount();
        if (location.pathname === "/my-orders/") location.href = "/";
      });
    } else {
      el.innerHTML = `<a href="/login/">Login</a>`;
    }
  } catch (e) { el.innerHTML = `<a href="/login/">Login</a>`; }
}
document.addEventListener("DOMContentLoaded", refreshAuthNav);
