// Intelliconz Accounting login v4 (web_include_js): minimal centred sign-in. The brand panel was removed at Zain's request.
// Adds the body class that scopes css/kodenova_login.css, puts the official Intelliconz Accounting wordmark above the form
// and swaps the big "Sign In" heading for a small "Welcome back". Progressive: login still works without it.
(function () {
  "use strict";
  var LANG = (document.documentElement.lang || "en").slice(0, 2);
  var T = {
    en: { welcome: "Welcome back", wsub: "Sign in to your Intelliconz Accounting account." },
    es: { welcome: "Te damos la bienvenida", wsub: "Inicia sesión en tu cuenta de Intelliconz Accounting." },
    ar: { welcome: "مرحبًا بعودتك", wsub: "سجّل الدخول إلى حسابك في Intelliconz Accounting." }
  };
  var S = T[LANG] || T.en;
  var IMG = "/assets/kodenova_theme/images/";

  function logoAll() {
    // every login-page section (login / forgot / signup) gets the wordmark in place of the settings logo
    document.querySelectorAll(".page-card-head").forEach(function (head) {
      if (head.querySelector(".kn-login-logo")) return;
      var row = head.querySelector(".kn-brand-row");
      if (!row) { row = document.createElement("div"); row.className = "kn-brand-row"; head.insertBefore(row, head.firstChild); }
      row.querySelectorAll("img").forEach(function (i) { i.remove(); });
      var img = new Image();
      img.className = "kn-login-logo"; img.alt = "Intelliconz Accounting"; img.width = 193; img.height = 40;
      img.src = IMG + "kodeerp-logo.png";
      img.srcset = IMG + "kodeerp-logo@1x.png 1x, " + IMG + "kodeerp-logo.png 2x, " + IMG + "kodeerp-logo@4x.png 4x";
      row.insertBefore(img, row.firstChild);
      head.querySelectorAll(":scope > img").forEach(function (i) { i.remove(); });
    });
  }
  function formCopy() {
    var head = document.querySelector(".for-login .page-card-head");
    if (!head) return;
    var h = head.querySelector("h4"), sub = head.querySelector(".page-card-subtitle");
    if (h) h.textContent = S.welcome;
    if (sub) sub.textContent = S.wsub;
  }
  function boot() {
    if (!document.body || document.body.dataset.path !== "login") return;
    document.body.classList.add("kn-login-v2", "kn-login-v4");
    logoAll(); formCopy();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
