/* Shared storefront logic: fetch() + low-DOM rendering. No business logic in HTML. */
const API = "/api";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

async function api(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}

async function apiPost(path, body) {
  const r = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || `API ${r.status}`);
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
