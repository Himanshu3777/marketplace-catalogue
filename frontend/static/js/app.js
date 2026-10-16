/* Shared storefront logic: fetch() + low-DOM rendering. No business logic in HTML. */
const API = "/api";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

async function api(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
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
  const form = $("#search-form");
  if (form) form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = $("#search-input").value.trim();
    if (q) location.href = "/search/?q=" + encodeURIComponent(q);
  });
});
