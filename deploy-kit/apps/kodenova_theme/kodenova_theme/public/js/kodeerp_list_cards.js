// KodeERP list KPI cards (kodenova_theme v0.6: + mini charts, trend chips, icon micro-motion). Owned by the dashboard worker.
// One generic, config-driven strip of 4 brand KPI cards above the main list views.
// - Numbers: ONE batched call per list refresh to kodenova_theme.api.list_cards.get_list_cards,
//   which uses frappe.get_list on the server (role + user permissions apply; no raw SQL).
// - Cards follow the list's current filters; clicking a card toggles its filter on the list.
// - Hook: wraps frappe.views.ListView.prototype.refresh (a supported client extension point; no
//   core file is edited). The list bundle can load lazily, so the wrap is applied when it appears.
// - Styles live in css/kodeerp_dashboard.css (.kd-list-cards / .kd-card). Every string uses __().
(() => {
	"use strict";
	const METHOD = "kodenova_theme.api.list_cards.get_list_cards";
	// v6: mini charts load in a SECOND call after the cards paint (never blocks the list)
	const SERIES = "kodenova_theme.api.list_card_series.get_list_card_series";
	const seriesCache = new Map(); // key -> promise, for the life of the page (cleared on list_update)
	const DOCTYPES = new Set([
		"Sales Invoice", "Purchase Invoice", "Sales Order", "Quotation", "Customer", "Supplier",
		"Item", "Payment Entry", "Journal Entry", "Stock Entry", "Delivery Note", "Purchase Order",
	]);
	const TTL = 30 * 1000;
	const cache = new Map(); // key -> {t, promise}

	const esc = (s) => frappe.utils.escape_html(String(s == null ? "" : s));
	const keyOf = (dt, filters) => dt + "|" + JSON.stringify(filters || []);

	function fetchCards(dt, filters) {
		const key = keyOf(dt, filters);
		const hit = cache.get(key);
		if (hit && Date.now() - hit.t < TTL) return hit.promise;
		const promise = frappe
			.xcall(METHOD, { doctype: dt, filters: JSON.stringify(filters || []) })
			.catch(() => null);
		cache.set(key, { t: Date.now(), promise });
		return promise;
	}

	function fetchSeries(dt, filters) {
		const key = keyOf(dt, filters);
		if (!seriesCache.has(key)) {
			seriesCache.set(key, frappe.xcall(SERIES, { doctype: dt, filters: JSON.stringify(filters || []) }).catch(() => null));
		}
		return seriesCache.get(key);
	}

	function compact(value, currency, country) {
		const n = Number(value) || 0;
		if (Math.abs(n) < 100000) {
			return currency ? format_currency(n, currency, 0) : format_number(n, null, 0);
		}
		const parts = frappe.utils.shorten_number(n, country || frappe.sys_defaults.country, 5).split(" ");
		const head = currency ? format_currency(parseFloat(parts[0]), currency) : parts[0];
		return head + (parts[1] ? " " + parts[1] : "");
	}

	function fmt(value, fieldtype, currency, country) {
		if (value == null) return "";
		return fieldtype === "Currency" ? compact(value, currency, country) : format_number(value, null, 0);
	}

	// v5: one line icon per card (24px grid, stroke = currentColor, accent dot = card tone)
	const P = {
		up: '<path d="M4 16l5-5 4 4 7-7"/><path d="M15 8h5v5"/>',
		clock: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
		alert: '<path d="M12 4l9 16H3z"/><path d="M12 10v4"/><circle class="kd-dot" cx="12" cy="17" r="1.3"/>',
		check: '<circle cx="12" cy="12" r="8"/><path d="M8.5 12.5l2.5 2.5 4.5-5"/>',
		users: '<circle cx="9" cy="9" r="3.2"/><path d="M3.5 19c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5"/><path d="M15.5 6.2a3 3 0 010 5.6M17 14.8c1.7.6 3 1.9 3.5 4.2"/>',
		box: '<path d="M4 8l8-4 8 4v8l-8 4-8-4z"/><path d="M4 8l8 4 8-4M12 12v8"/>',
		wallet: '<path d="M4 7h14a2 2 0 012 2v8a2 2 0 01-2 2H4z"/><path d="M4 7V6a2 2 0 012-2h10"/><circle class="kd-dot" cx="16" cy="13" r="1.4"/>',
		doc: '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
		bank: '<path d="M3 9l9-5 9 5"/><path d="M5 10v7M9.5 10v7M14.5 10v7M19 10v7M3 20h18"/>',
		swap: '<path d="M5 8h13l-3-3M19 16H6l3 3"/>',
		inbox: '<path d="M12 4v10M8 10l4 4 4-4"/><path d="M4 15v4h16v-4"/>',
		outbox: '<path d="M12 14V4M8 8l4-4 4 4"/><path d="M4 15v4h16v-4"/>',
	};
	const ICON = { billed_month: "up", month: "up", in: "inbox", out: "outbox", net: "wallet", value: "wallet",
		unpaid: "clock", open: "clock", to_fulfil: "box", to_bill: "doc", outstanding: "clock",
		overdue: "alert", lost: "alert", low: "alert", issue: "outbox", on_hold: "alert",
		paid: "check", completed: "check", won: "check", receipt: "inbox", transfer: "swap",
		total: "users", new: "users", companies: "bank", active: "box", stock: "box", drafts: "doc", bank: "bank", opening: "doc" };
	// micro-motion per glyph (CSS: [data-anim]); plays once on load and again on hover (~400ms)
	const ANIM = { up: "nudge", clock: "spin", alert: "pulse", check: "pop", users: "bob", box: "bob", wallet: "tilt",
		doc: "tilt", bank: "bob", swap: "swap", inbox: "drop", outbox: "lift" };
	const icon = (key) => {
		const g = P[ICON[key]] ? ICON[key] : "doc";
		return `<span class="kd-card-icon" aria-hidden="true" data-anim="${ANIM[g]}"><svg viewBox="0 0 24 24">${P[g]}</svg></span>`;
	};
	const reduceMotion = () => window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

	// format an in-between value the same way as the final one (keeps SAR / K / M style while counting)
	function fmtLike(v, c) {
		if (c.fieldtype !== "Currency") return format_number(Math.round(v), null, 0);
		if (Math.abs(Number(c.value) || 0) < 100000) return format_currency(Math.round(v), c.currency, 0);
		const parts = frappe.utils.shorten_number(v, c.country || frappe.sys_defaults.country, 5).split(" ");
		return format_currency(parseFloat(parts[0]), c.currency) + (parts[1] ? " " + parts[1] : "");
	}
	function countUp(el, c, from, delay) {
		const to = Number(c.value) || 0;
		const final = el.textContent;
		if (reduceMotion() || from === to || !isFinite(to)) return;
		const dur = 900, t0 = performance.now() + delay;
		el.textContent = fmtLike(from, c);
		const ease = (t) => 1 - Math.pow(1 - t, 3);
		const step = (now) => {
			if (!el.isConnected) return;
			const t = Math.min(1, Math.max(0, (now - t0) / dur));
			el.textContent = t >= 1 ? final : fmtLike(from + (to - from) * ease(t), c);
			if (t < 1) requestAnimationFrame(step);
		};
		requestAnimationFrame(step);
	}

	function wrapperFor(listview) {
		let $w = listview.page.wrapper.find(".kd-list-cards");
		if (!$w.length) {
			$w = $(`<section class="kd-list-cards" aria-label="${esc(__("Summary"))}" aria-live="polite"></section>`);
			const $anchor = listview.page.wrapper.find(".layout-main-section-wrapper").first();
			if ($anchor.length) $w.prependTo($anchor);
			else $w.prependTo(listview.$frappe_list);
		}
		return $w;
	}

	function skeleton($w) {
		if ($w.children(".kd-card").length) {
			$w.children(".kd-card").addClass("is-loading");
			return;
		}
		$w.html(
			Array.from({ length: 4 }, () =>
				`<div class="kd-card is-loading" aria-hidden="true">
					<span class="kd-card-top"><span class="kd-card-label">&nbsp;</span><span class="kd-card-icon"><svg viewBox="0 0 24 24"></svg></span></span>
					<span class="kd-card-mid"><span class="kd-card-value">&nbsp;</span><span class="kd-viz is-loading"></span></span>
					<span class="kd-card-foot"><span class="kd-card-sub">&nbsp;</span></span>
				</div>`
			).join("")
		);
	}

	const sameFilter = (a, b) =>
		a[1] === b[0] && a[2] === b[1] && JSON.stringify(a[3]) === JSON.stringify(b[2]);

	function isActive(listview, cardFilters) {
		if (!cardFilters || !cardFilters.length) return false;
		const current = listview.get_filters_for_args() || [];
		return cardFilters.every((cf) => current.some((f) => sameFilter(f, cf)));
	}

	async function toggle(listview, card) {
		const area = listview.filter_area;
		if (!area || !card.filters || !card.filters.length) return;
		const fields = [...new Set(card.filters.map((f) => f[0]))];
		const active = isActive(listview, card.filters);
		for (const field of fields) await area.remove(field);
		if (!active) await area.add(card.filters.map((f) => [listview.doctype, f[0], f[1], f[2]]));
	}

	function render(listview, $w, data) {
		const cards = (data && data.cards ? data.cards : []).filter((c) => c.value != null);
		if (!cards.length) {
			$w.attr("hidden", true).empty();
			return;
		}
		$w.removeAttr("hidden");
		const html = cards.map((c, i) => {
			const value = fmt(c.value, c.fieldtype, c.currency, c.country);
			const zero = !Number(c.value);
			let sub = "";
			if (c.sub_label) {
				const arg = c.sub != null ? fmt(c.sub, c.sub_fieldtype, c.currency, c.country) : c.sub_arg != null ? c.sub_arg : "";
				sub = c.sub_label.replace("{0}", arg);
			}
			if (zero && !sub) sub = __("Nothing here yet");
			const clickable = c.filters && c.filters.length;
			const active = clickable && isActive(listview, c.filters);
			const tag = clickable ? "button" : "div";
			const title = clickable
				? active ? __("Click to clear this filter") : __("Click to filter the list")
				: "";
			return `<${tag} class="kd-card${active ? " is-active" : ""}" data-i="${i}" data-tone="${esc(c.tone)}"
				${clickable ? `type="button" aria-pressed="${active ? "true" : "false"}"` : ""} ${title ? `title="${esc(title)}"` : ""}>
				<span class="kd-card-top"><span class="kd-card-label">${esc(c.label)}</span>${icon(c.key)}</span>
				<span class="kd-card-mid"><span class="kd-card-value${zero ? " kd-card-empty" : " is-nonzero"}">${esc(value)}</span><span class="kd-viz is-loading" aria-hidden="true"></span></span>
				<span class="kd-card-foot"><span class="kd-card-sub${sub ? " kd-sub-in" : ""}">${esc(sub)}</span></span>
			</${tag}>`;
		});
		const prev = $w.data("kd-prev") || {};
		const firstPaint = !$w.hasClass("kd-settled");
		$w.html(html.join(""));
		// count up from 0 on first paint, from the old number when a filter changes the value
		$w.find(".kd-card-value").each(function (i) {
			const c = cards[i];
			const from = firstPaint ? 0 : (prev[c.key] != null ? prev[c.key] : 0);
			if (!firstPaint && prev[c.key] === Number(c.value)) { $(this).closest(".kd-card").find(".kd-card-sub").removeClass("kd-sub-in"); return; }
			countUp(this, c, from, firstPaint ? 120 + i * 80 : 0);
		});
		$w.data("kd-prev", Object.fromEntries(cards.map((c) => [c.key, Number(c.value) || 0])));
		if (firstPaint) setTimeout(() => $w.addClass("kd-settled"), 1200);
		else $w.find(".kd-card-icon").attr("data-played", "1");
		// charts: second call; drawn after the count-up has landed (staggered)
		const t0 = performance.now(), key = $w.attr("data-key");
		fetchSeries(listview.doctype, listview.get_filters_for_args ? listview.get_filters_for_args() : [])
			.then((res) => { if ($w.attr("data-key") === key) paintViz($w, cards, res, firstPaint, t0); })
			.catch(() => paintViz($w, cards, null, firstPaint, t0));
		$w.find("button.kd-card").on("click", function () {
			toggle(listview, cards[Number(this.dataset.i)]);
		});
	}

	// ------------------------------------------------------------------ v6 mini charts (inline SVG)
	const H = 34;
	let uid = 0;
	const monthLabel = (m) => {
		try {
			const lang = (frappe.boot && frappe.boot.lang) || "en";
			return new Intl.DateTimeFormat(lang + "-u-nu-latn", { month: "short", year: "numeric" }).format(new Date(m + "-15T12:00:00"));
		} catch (e) { return m; }
	};
	const pctText = (p) => format_number(p, null, p > 0 && p < 1 ? 1 : 0) + "%";

	function flat(w, why) {
		return `<svg class="kd-viz-svg kd-viz-flat" viewBox="0 0 ${w} ${H}" width="${w}" height="${H}" preserveAspectRatio="none" role="img" aria-label="${esc(why)}">
			<title>${esc(why)}</title><path d="M2 ${H - 4}H${w - 2}" pathLength="1"/></svg>`;
	}

	function tip(s, c) {
		return s.months.map((m, i) => monthLabel(m) + ": " + fmt(s.points[i], s.fieldtype, c.currency, c.country)).join("\n");
	}

	function line(s, c, w) {
		const pts = s.points.map(Number), n = pts.length;
		if (!n || pts.every((v) => !v)) return flat(w, __("No activity in the last 6 months"));
		const max = Math.max(...pts), min = Math.min(0, ...pts), span = max - min || 1;
		const xy = pts.map((v, i) => [2 + (i * (w - 4)) / (n - 1 || 1), 3 + (1 - (v - min) / span) * (H - 7)]);
		const d = xy.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join("");
		const id = "kdg" + ++uid, last = xy[n - 1];
		return `<svg class="kd-viz-svg kd-viz-line" viewBox="0 0 ${w} ${H}" width="${w}" height="${H}" preserveAspectRatio="none" role="img" aria-label="${esc(tip(s, c))}">
			<title>${esc(tip(s, c))}</title>
			<defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="currentColor" stop-opacity=".22"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient></defs>
			<path class="kd-viz-area" d="${d}L${last[0].toFixed(1)} ${H}L${xy[0][0].toFixed(1)} ${H}Z" fill="url(#${id})"/>
			<path class="kd-viz-stroke" d="${d}" pathLength="1"/>
			<circle class="kd-viz-dot" cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="2.6"/></svg>`;
	}

	function bars(s, c, w) {
		const pts = s.points.map(Number), n = pts.length;
		if (!n || pts.every((v) => !v)) return flat(w, __("No activity in the last 6 months"));
		const max = Math.max(0, ...pts), min = Math.min(0, ...pts), span = max - min || 1;
		const base = 2 + (max / span) * (H - 4), gap = 4, bw = Math.max(3, (w - gap * (n - 1)) / n);
		const rects = pts.map((v, i) => {
			const h = Math.max(v ? 2 : 1, (Math.abs(v) / span) * (H - 4));
			const y = v >= 0 ? base - h : base;
			return `<rect class="kd-viz-bar${v < 0 ? " is-neg" : ""}${v ? "" : " is-zero"}" x="${(i * (bw + gap)).toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" style="--kd-bi:${i}"/>`;
		}).join("");
		return `<svg class="kd-viz-svg kd-viz-bars" viewBox="0 0 ${w} ${H}" width="${w}" height="${H}" preserveAspectRatio="none" role="img" aria-label="${esc(tip(s, c))}">
			<title>${esc(tip(s, c))}</title>${rects}</svg>`;
	}

	function ring(s) {
		const den = Number(s.den) || 0, num = Number(s.num) || 0;
		const p = den > 0 ? Math.max(0, Math.min(100, (num / den) * 100)) : 0;
		const label = den > 0 ? pctText(Math.round(p * 10) / 10 >= 1 ? Math.round(p) : Math.round(p * 10) / 10) : "–";
		const why = den > 0 ? label + " · " + __(s.basis || "") : __("No data yet");
		return `<span class="kd-viz-ring${den > 0 ? "" : " kd-viz-flat"}" role="img" aria-label="${esc(why)}" title="${esc(why)}" style="--kd-p:${p.toFixed(2)}">
			<svg viewBox="0 0 36 36" width="${H}" height="${H}"><circle class="kd-ring-track" cx="18" cy="18" r="15" pathLength="100"/>
			<circle class="kd-ring-arc" cx="18" cy="18" r="15" pathLength="100" stroke-dasharray="${p.toFixed(2)} 100"/></svg>
			<b>${esc(label)}</b>${s.cap ? `<span class="kd-viz-cap">${esc(__(s.cap))}</span>` : ""}</span>`;
	}

	function meter(s) {
		const den = Number(s.den) || 0, num = Number(s.num) || 0;
		const p = den > 0 ? Math.max(0, Math.min(100, (num / den) * 100)) : 0;
		const label = den > 0 ? pctText(Math.round(p)) : "–";
		const why = den > 0 ? label + " · " + __(s.basis || "") : __("No data yet");
		return `<span class="kd-viz-meter${den > 0 ? "" : " kd-viz-flat"}" role="img" aria-label="${esc(why)}" title="${esc(why)}" style="--kd-p:${p.toFixed(2)}%">
			<span class="kd-viz-meter-top"><b>${esc(label)}</b>${s.cap ? `<span class="kd-viz-cap">${esc(__(s.cap))}</span>` : ""}</span><i><em></em></i></span>`;
	}

	function trendChip(s) {
		if (!s || s.trend == null || !isFinite(s.trend)) return "";
		const t = Math.round(Number(s.trend));
		const dir = t > 0 ? "up" : t < 0 ? "down" : "flat";
		const arrow = dir === "flat" ? '<path d="M2 6h8"/>' : dir === "up" ? '<path d="M6 10V2M2.5 5.5L6 2l3.5 3.5"/>' : '<path d="M6 2v8M2.5 6.5L6 10l3.5-3.5"/>';
		const num = (t > 0 ? "+" : t < 0 ? "−" : "") + format_number(Math.abs(t), null, 0) + "%";
		const basis = s.trend_basis === "vs last month-end" ? __("vs last month-end") : __("vs last month");
		return `<span class="kd-trend is-${dir}" title="${esc(num + " " + basis + (s.trend_basis === "vs same days last month" ? " (" + __("same days") + ")" : ""))}">
			<svg viewBox="0 0 12 12" aria-hidden="true">${arrow}</svg><bdi>${esc(num)}</bdi><span class="kd-trend-basis">${esc(basis)}</span></span>`;
	}

	function paintViz($w, cards, res, firstPaint, t0) {
		const series = (res && res.series) || {};
		const still = reduceMotion();
		$w.children(".kd-card").each(function (i) {
			const c = cards[i];
			const slot = this.querySelector(".kd-viz");
			if (!c || !slot) return;
			const s = series[c.key];
			const w = Math.round(slot.clientWidth) || 96;
			let html;
			if (!s) html = flat(w, __("No trend data"));
			else if (s.kind === "ring") html = ring(s);
			else if (s.kind === "meter") html = meter(s);
			else if (s.kind === "bars") html = bars(s, c, w);
			else html = line(s, c, w);
			const delay = firstPaint ? Math.max(0, 1050 + i * 90 - (performance.now() - t0)) : 40 + i * 60;
			slot.style.setProperty("--kd-d", Math.round(delay) + "ms");
			slot.className = "kd-viz kd-viz-" + (s ? s.kind : "none") + (still ? " is-still" : " is-in");
			slot.innerHTML = html;
			const chip = trendChip(s);
			const foot = this.querySelector(".kd-card-foot");
			if (foot) {
				foot.querySelectorAll(".kd-trend").forEach((n) => n.remove());
				if (chip) {
					foot.insertAdjacentHTML("beforeend", chip);
					foot.lastElementChild.style.animationDelay = Math.round(delay + 650) + "ms";
				}
			}
		});
	}

	function update(listview) {
		if (!listview || !DOCTYPES.has(listview.doctype)) return;
		if (listview.view_name && listview.view_name !== "List") return;
		if (!listview.page || !listview.page.wrapper) return;
		const $w = wrapperFor(listview);
		const filters = listview.get_filters_for_args ? listview.get_filters_for_args() : [];
		const key = keyOf(listview.doctype, filters);
		if ($w.attr("data-key") === key && $w.children(".kd-card:not(.is-loading)").length) {
			// same filters, already showing: refresh active states only
			$w.children("button.kd-card").each(function () {
				const card = $w.data("kd-cards")?.[Number(this.dataset.i)];
				if (card) $(this).toggleClass("is-active", isActive(listview, card.filters));
			});
			const hit = cache.get(key);
			if (hit && Date.now() - hit.t < TTL) return;
		}
		$w.attr("data-key", key);
		skeleton($w);
		fetchCards(listview.doctype, filters).then((data) => {
			if ($w.attr("data-key") !== key) return; // a newer refresh won
			$w.data("kd-cards", (data && data.cards ? data.cards : []).filter((c) => c.value != null));
			render(listview, $w, data);
		});
	}

	function patch() {
		const LV = frappe.views && frappe.views.ListView;
		if (!LV) return false;
		if (LV.prototype.__kdListCards) return true;
		const original = LV.prototype.refresh;
		LV.prototype.refresh = function (...args) {
			const out = original.apply(this, args);
			Promise.resolve(out).then(() => update(this)).catch(() => {});
			return out;
		};
		LV.prototype.__kdListCards = true;
		// a list opened before the patch landed
		if (window.cur_list && cur_list instanceof LV) update(cur_list);
		return true;
	}

	function boot() {
		if (patch()) return;
		let tries = 0;
		const timer = setInterval(() => {
			if (patch() || ++tries > 120) clearInterval(timer);
		}, 250);
	}

	$(document).on("app_ready", boot);
	if (window.frappe && frappe.boot && frappe.views) boot();
	// fresh numbers after a document in that list changes
	$(document).on("app_ready", () => {
		frappe.realtime && frappe.realtime.on("list_update", (d) => {
			if (!d || !DOCTYPES.has(d.doctype)) return;
			for (const k of [...cache.keys()]) if (k.startsWith(d.doctype + "|")) cache.delete(k);
			for (const k of [...seriesCache.keys()]) if (k.startsWith(d.doctype + "|")) seriesCache.delete(k);
		});
	});
	frappe.provide("kodeerp.list_cards");
	kodeerp.list_cards.refresh = (listview) => { cache.clear(); seriesCache.clear(); update(listview || window.cur_list); };
})();
