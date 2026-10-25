// Kodenova Theme for KodeERP — Desk bootstrap v0.4 (hooks.app_include_js). No core files changed.
(function () {
  window.kodenova_theme = { version: "0.4.0" };
  document.documentElement.classList.add("kodenova-theme");

  // Brand chart palette: ink-free, AA-distinct series in Kodenova colours.
  var KN_PALETTE = ["#2f6bff", "#ff6a3d", "#ffd23f", "#0e0e10", "#77a6ff", "#ffb199", "#c99400", "#6c6c74", "#1f49b8", "#c2410c"];
  // Upstream hex/named colours that some reports hard-code -> brand equivalents.
  var KN_MAP = {
    "#077ddf": "#2f6bff", "#0d8ef8": "#2f6bff", "#61afef": "#77a6ff", "#5e64ff": "#2f6bff", "#318ad8": "#2f6bff",
    "#28a745": "#2f6bff", "#70e078": "#2f6bff", "#48bb74": "#2f6bff", "#98d85b": "#77a6ff",
    "#ff5858": "#ff6a3d", "#fc4f51": "#ff6a3d", "#e24c4c": "#c2410c", "#ffa00a": "#ffd23f", "#f8814f": "#ff6a3d",
    "#ffc107": "#ffd23f", "#feef72": "#ffd23f", "#7cd6fd": "#77a6ff", "#743ee2": "#0e0e10", "#b554ff": "#ffb199",
    "#ff7846": "#ff6a3d", "#f683ae": "#ffb199", "#7575ff": "#77a6ff",
    "blue": "#2f6bff", "light-blue": "#77a6ff", "green": "#2f6bff", "light-green": "#77a6ff", "orange": "#ff6a3d",
    "red": "#c2410c", "yellow": "#ffd23f", "purple": "#0e0e10", "violet": "#0e0e10", "pink": "#ffb199", "grey": "#6c6c74", "gray": "#6c6c74",
  };
  function mapColor(c) {
    if (typeof c !== "string") return c;
    var k = c.trim().toLowerCase();
    return KN_MAP[k] || c;
  }
  function brandCharts() {
    if (!window.frappe || !frappe.utils || !frappe.Chart || frappe.Chart.__kn) return !!(window.frappe && frappe.Chart && frappe.Chart.__kn);
    frappe.utils.get_chart_palette = function () { return KN_PALETTE.slice(); };
    var Orig = frappe.Chart;
    var Branded = class extends Orig {
      constructor(parent, options) {
        options = options || {};
        if (Array.isArray(options.colors) && options.colors.length) options.colors = options.colors.map(mapColor);
        else if (options.type !== "heatmap") options.colors = KN_PALETTE.slice();
        super(parent, options);
      }
    };
    Branded.__kn = true;
    frappe.Chart = Branded;
    return true;
  }
  if (!brandCharts()) {
    var tries = 0, t = setInterval(function () { if (brandCharts() || ++tries > 100) clearInterval(t); }, 50);
  }

  // Status tint hook for the form header pill: expose the document status as data-kn-status
  // (list pills already carry data-filter="status,=,X").
  function tagFormPill(frm) {
    if (!frm || !frm.doc) return;
    var s = frm.doc.docstatus === 0 ? "Draft" : frm.doc.docstatus === 2 ? "Cancelled" : (frm.doc.status || "");
    document.querySelectorAll(".page-indicator-pill").forEach(function (el) { el.setAttribute("data-kn-status", s); });
  }
  // Route enter animation: only on desk page change (never on form refresh / typing).
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (window.jQuery && !reduce) {
    jQuery(document).on("page-change", function () {
      var pages = document.querySelectorAll(".page-container");
      var el = null;
      pages.forEach(function (p) { if (p.offsetParent !== null || getComputedStyle(p).display !== "none") el = p; });
      if (!el) return;
      el.classList.remove("kn-route-enter");
      void el.offsetWidth; // restart animation
      el.classList.add("kn-route-enter");
      clearTimeout(el.__knT);
      el.__knT = setTimeout(function () { el.classList.remove("kn-route-enter"); }, 400);
    });
  }
  if (window.jQuery) {
    jQuery(document).on("form-refresh", function (e, frm) { tagFormPill(frm); setTimeout(function () { tagFormPill(frm); }, 300); });
  }
})();

// ---- v0.5 white-label: KodeERP About dialog (replaces frappe.ui.misc.about at runtime; no core edit) ----
(function () {
  if (!window.frappe || !frappe.provide) return;
  frappe.provide("frappe.ui.misc");
  frappe.provide("frappe.ui.toolbar");
  var KN_VERSION = "0.5 (sandbox)";
  frappe.ui.misc.about = function () {
    if (frappe.ui.misc.kn_about_dialog) { frappe.ui.misc.kn_about_dialog.show(); return; }
    var d = new frappe.ui.Dialog({ title: __("About") });
    $(d.wrapper).addClass("about-dialog kn-about");
    $(d.body).html(
      '<div class="kn-about-body">' +
        '<img src="/assets/kodenova_theme/images/kodeerp-icon-128.png" alt="" class="kn-about-mark">' +
        '<div class="kn-about-name">Kode<span>ERP</span></div>' +
        '<p class="kn-about-tag">' + __("Business management by Kodenova.") + '</p>' +
        '<div class="kn-about-row"><span>' + __("Version") + '</span><b>' + KN_VERSION + '</b></div>' +
        '<div class="kn-about-row"><span>' + __("Website") + '</span><a href="https://kodenova.com" target="_blank" rel="noopener">kodenova.com</a></div>' +
        '<p class="kn-about-legal">' + __("KodeERP includes open-source software.") +
        ' <a href="/licenses" target="_blank">' + __("Open-source licenses") + '</a></p>' +
      '</div>'
    );
    frappe.ui.misc.kn_about_dialog = d;
    d.show();
  };
  frappe.ui.toolbar.show_about = function () { frappe.ui.misc.about(); };
})();

// ---- v0.5 white-label: drop upstream promotional sidebar banners (CRM / Helpdesk ads) ----
(function () {
  function patch() {
    var S = window.frappe && frappe.ui && frappe.ui.Sidebar;
    if (!S || S.prototype.__knPatched) return !!S;
    ["get_crm_banner", "get_helpdesk_banner"].forEach(function (m) { if (S.prototype[m]) S.prototype[m] = function () {}; });
    S.prototype.__knPatched = true;
    return true;
  }
  if (!patch() && window.jQuery) jQuery(function () { patch(); });
})();

// ---- v0.5 spec reveal (§3) for desk: [data-ani]/.fade/.reveal-lines get .in on view; 3s safety timeout.
// Entrance-only (no loops); data screens never get these attributes unless a widget opts in.
(function () {
  function knRevealDesk() {
    var root = document.documentElement;
    root.classList.add("js");
    var els = document.querySelectorAll("[data-ani]:not(.in), .kn-fade:not(.in), .reveal-lines:not(.in)");
    if (!els.length) return;
    if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.1 });
    els.forEach(function (e) { io.observe(e); });
    setTimeout(function () { els.forEach(function (e) { e.classList.add("in"); }); }, 3000);
  }
  window.knReveal = window.knReveal || knRevealDesk;
  if (window.jQuery) {
    jQuery(function () { knRevealDesk(); });
    jQuery(document).on("page-change", function () { setTimeout(knRevealDesk, 50); });
  }
})();

// ---- v0.5 white-label: browser tab titles never show upstream product names ----
(function () {
  var RX = /\bERPNext\b|\bFrappe HR\b|\bFrappe\b/g;
  var MAP = { "ERPNext": "KodeERP", "Frappe HR": "KodeERP People", "Frappe": "KodeERP" };
  function fix() { var t = document.title; if (RX.test(t)) { RX.lastIndex = 0; document.title = t.replace(RX, function (m) { return MAP[m]; }); } RX.lastIndex = 0; }
  var el = document.querySelector("title");
  if (el && window.MutationObserver) new MutationObserver(fix).observe(el, { childList: true, characterData: true, subtree: true });
  fix();
})();

// ---- v0.5 i18n: language switcher (user menu → "Language"). Updates the user's own profile, then reloads.
frappe.provide("kodeerp");
kodeerp.switch_language = function () {
  var langs = [["en", "English"], ["es", "Español"], ["ar", "العربية"]];
  var d = new frappe.ui.Dialog({
    title: __("Switch language"),
    fields: [
      { fieldtype: "HTML", options: '<p class="text-muted">' + __("Choose the language for KodeERP. The page reloads to apply it.") + "</p>" },
      { fieldname: "language", fieldtype: "Select", label: __("Language"), default: frappe.boot.lang || "en",
        options: langs.map(function (l) { return { value: l[0], label: l[1] }; }) },
    ],
    primary_action_label: __("Apply"),
    primary_action: function (v) {
      frappe.xcall("frappe.client.set_value", { doctype: "User", name: frappe.session.user, fieldname: "language", value: v.language })
        .then(function () { d.hide(); frappe.ui.toolbar.clear_cache ? frappe.ui.toolbar.clear_cache() : window.location.reload(); });
    },
  });
  d.show();
};

// ---- v0.5 white-label: strip upstream documentation links from field help text (all languages) ----
(function () {
  var SEL = '.frappe-control a[href*="frappe.io"], .frappe-control a[href*="erpnext.com"], .frappe-control a[href*="frappeframework.com"],' +
    '.help-box a[href*="frappe.io"], .help-box a[href*="erpnext.com"], .form-dashboard a[href*="docs.frappe.io"],' +
    '.onboarding-step-description a[href*="frappe.io"], .page-menu a[href*="docs.frappe.io"], .dropdown-menu a[href*="docs.frappe.io"]';
  var DOCWORD = /documentation|documentación|التوثيق|الوثائق|docs|learn more|read more|más información|leer más|click here|haga clic|اضغط هنا/i;
  function clean(root) {
    (root || document).querySelectorAll(SEL).forEach(function (a) {
      var li = a.closest(".dropdown-item, li");
      if (li && li.closest(".dropdown-menu, .page-menu")) { li.remove(); return; }
      if (DOCWORD.test(a.textContent)) a.remove(); else a.replaceWith(document.createTextNode(a.textContent));
    });
  }
  window.kn_clean_doc_links = clean;
  if (window.jQuery) {
    jQuery(document).on("form-refresh page-change", function () { setTimeout(clean, 60); setTimeout(clean, 600); });
    jQuery(function () { setTimeout(clean, 800); });
  }
})();
