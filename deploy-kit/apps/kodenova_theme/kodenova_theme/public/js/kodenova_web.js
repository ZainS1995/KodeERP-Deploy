// Intelliconz Accounting website/login enhancements (web_include_js). Progressive: does nothing if markup changes.
// Guest pages: strings chosen by <html lang> (en / es / ar). Keep in sync with translations/*.csv.
var KN_L = (document.documentElement.lang || "en").slice(0, 2);
var KN_T = {
  en: { eyebrow: "Business management", l1: "Your ERP. Your data.", l2: 'Your business, <span class="hl">ready to <em class="kn-serif">grow</em></span>', cta: "Kodenova", tag: "by Kodenova", lic: "Open-source licenses", tl: 'Your ERP. Your data. <span class="kn-hl">Your business.</span>',
    sub: "Accounting, sales, inventory and e-invoicing in one place.", b1: "Built for e-invoicing", b2: "English, Spanish and Arabic", b3: "Real-time dashboards" },
  es: { eyebrow: "Gestión empresarial", l1: "Tu ERP. Tus datos.", l2: 'Tu negocio, <span class="hl">listo para <em class="kn-serif">crecer</em></span>', cta: "Kodenova", tag: "por Kodenova", lic: "Licencias de código abierto", tl: 'Tu ERP. Tus datos. <span class="kn-hl">Tu negocio.</span>',
    sub: "Contabilidad, ventas, inventario y facturación electrónica en un solo lugar.", b1: "Diseñado para la facturación electrónica", b2: "En español, inglés y árabe", b3: "Paneles en tiempo real" },
  ar: { eyebrow: "نظام تخطيط موارد المؤسسات", l1: "نظامك. بياناتك.", l2: '<span class="hl">أعمالك، جاهزة للنمو.</span>', cta: "كودنوفا", tag: "من كودنوفا", lic: "تراخيص المصادر المفتوحة", tl: 'نظامك. بياناتك. <span class="kn-hl">أعمالك.</span>',
    sub: "المحاسبة والمبيعات والمخزون والفوترة الإلكترونية في مكان واحد.", b1: "مصمم للفوترة الإلكترونية", b2: "بالعربية والإنجليزية والإسبانية", b3: "لوحات معلومات لحظية" }
};
var KN_S = KN_T[KN_L] || KN_T.en;
// Spec reveal script (§3): IntersectionObserver adds .in (threshold .1); 3s safety timeout reveals everything.
function knReveal() {
  var root = document.documentElement;
  root.classList.remove("no-js"); root.classList.add("js");
  var els = document.querySelectorAll("[data-ani], .kn-fade, .reveal-lines");
  if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { threshold: 0.1 });
  els.forEach(function (e) { if (!e.classList.contains("in")) io.observe(e); });
  setTimeout(function () { document.querySelectorAll("[data-ani], .kn-fade, .reveal-lines").forEach(function (e) { e.classList.add("in"); }); }, 3000);
}
window.knReveal = knReveal;
(function () {
  function brandLogin() {
    if (document.body.dataset.path !== "login") return;
    document.querySelectorAll(".page-card-head").forEach(function (head) {
      if (head.querySelector(".kn-brand")) return;
      var img = head.querySelector("img");
      // the site logo setting is the full lockup (used by email / update-password); here the mark sits beside live text
      if (img) img.src = "/assets/kodenova_theme/images/kodeerp-logo.png";
      var brand = document.createElement("div");
      brand.className = "kn-brand";
      brand.setAttribute("aria-label", "Intelliconz Accounting");
      brand.innerHTML = '<span class="kn-brand-name">Kode<span class="kn-brand-accent">ERP</span></span><span class="kn-brand-tag">' + KN_S.tag + '</span>';
      if (img && img.parentNode) {
        var row = document.createElement("div");
        row.className = "kn-brand-row";
        img.parentNode.insertBefore(row, img);
        row.appendChild(img);
        row.appendChild(brand);
      } else {
        head.insertBefore(brand, head.firstChild);
      }
      if (!head.querySelector(".kn-tagline")) {
        var tag = document.createElement("p");
        tag.className = "kn-tagline";
        tag.innerHTML = KN_S.tl;
        var after = head.querySelector(".kn-brand-row") || head.querySelector(".kn-brand");
        if (after && after.parentNode === head) head.insertBefore(tag, after.nextSibling); else head.appendChild(tag);
      }
    });
    if (!document.querySelector(".kn-attribution")) {
      var note = document.createElement("p");
      note.className = "kn-attribution";
      note.innerHTML = '<a href="/licenses">' + KN_S.lic + '</a>';
      var host = document.getElementById("page-login") || document.querySelector(".page-content-wrapper");
      if (host) host.appendChild(note);
    }
  }
  // v3 split-screen login (brand panel, dashboard preview, motion) lives in js/kodenova_login.js.
  // Branded message / error / 403 pages: add the Intelliconz Accounting mark above the card title.
  function brandMessage() {
    var path = document.body.dataset.path;
    if (path !== "message" && path !== "error") return;
    var head = document.querySelector(".page-card-head");
    if (head && !head.querySelector(".kn-msg-mark")) {
      var img = document.createElement("img"); img.className = "kn-msg-mark"; img.alt = "Intelliconz Accounting";
      img.src = "/assets/kodenova_theme/images/kodeerp-logo.png"; head.insertBefore(img, head.firstChild);
    }
  }
  function boot() { brandLogin(); brandMessage(); knReveal(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
