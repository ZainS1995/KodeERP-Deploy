// KodeERP v5 form tabs: one ink box that slides/resizes from the previous tab to the clicked tab,
// the new tab's content fades/slides in, and the sticky tab bar gets a shadow while it is stuck.
// Works on every form (it only looks for .form-tabs-list .form-tabs), mirrors itself in RTL because
// it measures physical positions, and does nothing animated under prefers-reduced-motion.
// No core file is edited; styles live in css/kodeerp_v5.css.
(() => {
	"use strict";
	const reduce = window.matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };
	const bars = new WeakSet();

	function ink(ul) {
		let el = ul.querySelector(":scope > .kn-tab-ink");
		if (!el) {
			el = document.createElement("span");
			el.className = "kn-tab-ink";
			el.setAttribute("aria-hidden", "true");
			ul.prepend(el);
			ul.classList.add("kn-tabs-ink");
		}
		return el;
	}

	function place(ul, animate) {
		const el = ink(ul);
		const a = ul.querySelector(".nav-link.active");
		if (!a || !a.offsetParent || !a.offsetWidth) { el.style.opacity = "0"; return; }
		const instant = !animate || reduce.matches || el.style.opacity !== "1";
		if (instant) el.classList.add("kn-no-anim");
		el.style.width = a.offsetWidth + "px";
		el.style.height = a.offsetHeight + "px";
		el.style.transform = `translate(${a.offsetLeft}px, ${a.offsetTop}px)`;
		el.style.opacity = "1";
		if (instant) { void el.offsetWidth; el.classList.remove("kn-no-anim"); }
	}

	function paneIn(ul, fromEnd) {
		if (reduce.matches) return;
		const a = ul.querySelector(".nav-link.active");
		const sel = a && (a.getAttribute("href") || a.dataset.target || "");
		const root = ul.closest(".form-layout") || document;
		let pane = null;
		if (sel && sel.startsWith("#")) { try { pane = root.querySelector(sel); } catch (e) { pane = null; } }
		pane = pane || root.querySelector(".form-tab-content > .tab-pane.active");
		if (!pane) return;
		pane.classList.remove("kn-pane-in", "kn-from-end");
		void pane.offsetWidth;
		pane.classList.toggle("kn-from-end", !!fromEnd);
		pane.classList.add("kn-pane-in");
		pane.addEventListener("animationend", () => pane.classList.remove("kn-pane-in", "kn-from-end"), { once: true });
	}

	function watch(ul) {
		if (bars.has(ul)) return;
		bars.add(ul);
		place(ul, false);
		let last = ul.querySelector(".nav-link.active");
		new MutationObserver((muts) => {
			if (muts.every((m) => m.target.classList && m.target.classList.contains("kn-tab-ink"))) return;
			const now = ul.querySelector(".nav-link.active");
			if (now && now !== last) {
				const links = [...ul.querySelectorAll(".nav-link")];
				const backwards = last && links.indexOf(now) < links.indexOf(last);
				last = now;
				requestAnimationFrame(() => { place(ul, true); paneIn(ul, backwards); });
			} else {
				requestAnimationFrame(() => place(ul, false)); // tabs shown/hidden or relabelled
			}
		}).observe(ul, { subtree: true, attributes: true, attributeFilter: ["class", "style"], childList: true, characterData: true });
		if (window.ResizeObserver) new ResizeObserver(() => place(ul, false)).observe(ul);
		// sticky shadow
		const bar = ul.closest(".form-tabs-list");
		if (bar && window.IntersectionObserver) {
			const probe = document.createElement("div");
			probe.style.cssText = "height:1px;margin-bottom:-1px;pointer-events:none";
			bar.before(probe);
			new IntersectionObserver(([e]) => bar.classList.toggle("kn-stuck", !e.isIntersecting && e.boundingClientRect.top < e.rootBounds.bottom),
				{ rootMargin: "-120px 0px 0px 0px" }).observe(probe);
		}
	}

	function scan() { document.querySelectorAll(".form-tabs-list .form-tabs").forEach(watch); }

	let pending = false;
	const later = () => { if (pending) return; pending = true; setTimeout(() => { pending = false; scan(); }, 120); };
	$(document).on("form-refresh form-load app_ready page-change", later);
	window.addEventListener("load", later);
	if (window.frappe && frappe.router && frappe.router.on) frappe.router.on("change", later);
	// forms are built lazily; watch the page container for new tab bars (cheap: only childList at body level is checked)
	const root = document.body || document.documentElement;
	new MutationObserver((muts) => { for (const m of muts) if (m.addedNodes.length) { later(); break; } })
		.observe(root, { childList: true, subtree: true });
	window.addEventListener("resize", () => document.querySelectorAll(".form-tabs-list .form-tabs.kn-tabs-ink").forEach((ul) => place(ul, false)));
	later();
})();
