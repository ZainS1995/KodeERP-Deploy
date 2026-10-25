// KodeERP: item and tax lines follow the header Cost Centre / Branch live on the desk form.
// Mirrors kodenova_theme.accounting.line_dimensions (server rule, which is authoritative on save):
// Branch also sets the header Cost Centre from the site mapping kodeerp_branch_cost_centers.
// a line is updated when it is empty, still on the company default, or still on the previous header
// value; a line the user set to another value is left alone. Toggle: site_config kodeerp_sync_line_dimensions.
(() => {
	const DOCTYPES = ["Sales Invoice", "Purchase Invoice", "POS Invoice", "Sales Order", "Delivery Note", "Purchase Order", "Purchase Receipt"];
	const TABLES = ["items", "taxes"];
	const cfg = {};
	const config = (frm) => {
		const c = frm.doc.company;
		if (!c) return Promise.resolve(null);
		if (!cfg[c]) cfg[c] = frappe.xcall("kodenova_theme.accounting.line_dimensions.client_config", { company: c }).catch(() => ({ enabled: false, defaults: {} }));
		return cfg[c];
	};
	const remember = (frm) => {
		frm._kd_prev = frm._kd_prev || {};
		["cost_center", "branch"].forEach((f) => (frm._kd_prev[f] = frm.doc[f]));
	};
	async function sync(frm, field, onlyRow, prevOverride) {
		if (frm.doc.docstatus !== 0) return;
		const c = await config(frm);
		if (!c || !c.enabled) return;
		const hv = frm.doc[field], dv = (c.defaults || {})[field], prev = prevOverride !== undefined ? prevOverride : (frm._kd_prev || {})[field];
		if (!hv) return;
		let touched = false;
		for (const t of TABLES) {
			if (!frm.fields_dict[t]) continue;
			for (const row of frm.doc[t] || []) {
				if (onlyRow && row.name !== onlyRow) continue;
				if (!frappe.meta.has_field(row.doctype, field)) continue;
				const v = row[field];
				const follow = !v || (dv && v === dv && hv !== dv) || (prev && v === prev && v !== hv);
				if (follow && v !== hv) { row[field] = hv; touched = true; }
			}
			if (touched) frm.refresh_field(t);
		}
		if (touched) frm.dirty();
	}
	const all = (frm) => Promise.all(["cost_center", "branch"].map((f) => sync(frm, f)));
	const handlers = {
		onload_post_render: remember,
		refresh: remember,
		cost_center: (frm) => sync(frm, "cost_center").then(() => remember(frm)),
		branch: async (frm) => {
			const prevBranch = (frm._kd_prev || {}).branch;
			try {
				const c = await config(frm);
				if (c && c.branch_cc && frm.doc.docstatus === 0 && frappe.meta.has_field(frm.doctype, "cost_center")) {
					// header Cost Centre follows the Branch (site mapping) when empty, on the company default,
					// or still on the previous branch's cost centre; a deliberately different one is kept
					const map = c.branch_cost_centers || {}, target = map[frm.doc.branch], cur = frm.doc.cost_center;
					const dv = (c.defaults || {}).cost_center, prevAuto = prevBranch ? map[prevBranch] : null;
					if (target && target !== cur && (!cur || cur === dv || (prevAuto && cur === prevAuto))) await frm.set_value("cost_center", target);
				}
			} catch (e) { console.warn("KodeERP branch cost centre", e); }
			await sync(frm, "branch", null, prevBranch);
			remember(frm);
		},
		taxes_and_charges: (frm) => setTimeout(() => all(frm), 800), // after ERPNext loads the template rows
		before_save: (frm) => all(frm),
	};
	DOCTYPES.forEach((dt) => frappe.ui.form.on(dt, handlers));
	// new / changed item lines pick up the header values
	const rowHandlers = {
		item_code: (frm, cdt, cdn) => setTimeout(() => Promise.all(["cost_center", "branch"].map((f) => sync(frm, f, cdn))), 600),
	};
	["Sales Invoice Item", "Purchase Invoice Item", "POS Invoice Item", "Sales Order Item", "Delivery Note Item", "Purchase Order Item", "Purchase Receipt Item"].forEach((dt) => frappe.ui.form.on(dt, rowHandlers));
})();
