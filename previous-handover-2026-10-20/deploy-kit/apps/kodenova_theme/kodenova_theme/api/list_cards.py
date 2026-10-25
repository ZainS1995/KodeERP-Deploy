"""KPI cards shown above the main list views (kodeerp_list_cards.js).

One batched, permission-respecting call per list refresh: every figure comes from
frappe.get_list, so role permissions, user permissions and sharing all apply. No raw SQL.

Each card = filters (relative-date tokens resolved here) + a metric. The cards are ANDed with
the list's current filters, except on fields the card itself filters (the card's own filter
wins there), so a card keeps its meaning while the list is narrowed by customer, company, etc.
"""

import json

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, getdate, nowdate

THIS_MONTH = "__this_month__"

# metric: ("count",) | ("sum", field) ; sub: optional second metric shown under the value
# filters: [[field, op, value], ...] ; tone: ok | warn | ink | (default yellow)
INVOICE = lambda party_total: [  # noqa: E731
	{"key": "billed_month", "label": "Billed this month", "tone": "ok",
	 "filters": [["docstatus", "=", 1], ["posting_date", "Timespan", "this month"]],
	 "metric": ["sum", party_total], "sub": ["count"], "sub_label": "{0} invoices"},
	{"key": "unpaid", "label": "Unpaid", "tone": "",
	 "filters": [["docstatus", "=", 1], ["status", "in", ["Unpaid", "Partly Paid"]]],
	 "metric": ["sum", "outstanding_amount"], "sub": ["count"], "sub_label": "{0} open"},
	{"key": "overdue", "label": "Overdue", "tone": "warn",
	 "filters": [["docstatus", "=", 1], ["status", "=", "Overdue"]],
	 "metric": ["sum", "outstanding_amount"], "sub": ["count"], "sub_label": "{0} overdue"},
	{"key": "paid", "label": "Paid", "tone": "ok",
	 "filters": [["docstatus", "=", 1], ["status", "=", "Paid"]],
	 "metric": ["sum", party_total], "sub": ["count"], "sub_label": "{0} paid"},
]

ORDER = [
	{"key": "month", "label": "Ordered this month", "tone": "ok",
	 "filters": [["docstatus", "=", 1], ["transaction_date", "Timespan", "this month"]],
	 "metric": ["sum", "base_grand_total"], "sub": ["count"], "sub_label": "{0} orders"},
	{"key": "to_fulfil", "label": "To deliver", "tone": "",
	 "filters": [["docstatus", "=", 1], ["status", "in", ["To Deliver and Bill", "To Deliver"]]],
	 "metric": ["count"], "sub": ["sum", "base_grand_total"], "sub_label": "{0}"},
	{"key": "to_bill", "label": "To bill", "tone": "warn",
	 "filters": [["docstatus", "=", 1], ["status", "in", ["To Deliver and Bill", "To Bill"]]],
	 "metric": ["count"], "sub": ["sum", "base_grand_total"], "sub_label": "{0}"},
	{"key": "completed", "label": "Completed", "tone": "ink",
	 "filters": [["docstatus", "=", 1], ["status", "=", "Completed"]],
	 "metric": ["count"], "sub": ["sum", "base_grand_total"], "sub_label": "{0}"},
]

PURCHASE_ORDER = json.loads(json.dumps(ORDER))
PURCHASE_ORDER[1].update(label="To receive", filters=[["docstatus", "=", 1], ["status", "in", ["To Receive and Bill", "To Receive"]]])
PURCHASE_ORDER[2].update(filters=[["docstatus", "=", 1], ["status", "in", ["To Receive and Bill", "To Bill"]]])

POSTED_MONTH = lambda date_field, total, label="Posted this month": {  # noqa: E731
	"key": "month", "label": label, "tone": "ok",
	"filters": [["docstatus", "=", 1], [date_field, "Timespan", "this month"]],
	"metric": ["sum", total] if total else ["count"], "sub": ["count"] if total else None, "sub_label": "{0} entries"}
DRAFTS = {"key": "drafts", "label": "Drafts", "tone": "", "filters": [["docstatus", "=", 0]], "metric": ["count"]}

CONFIG = {
	"Sales Invoice": INVOICE("base_grand_total"),
	"Purchase Invoice": INVOICE("base_grand_total"),
	"Sales Order": ORDER,
	"Purchase Order": PURCHASE_ORDER,
	"Quotation": [
		{"key": "open", "label": "Open", "tone": "", "filters": [["docstatus", "=", 1], ["status", "in", ["Open", "Replied"]]],
		 "metric": ["sum", "base_grand_total"], "sub": ["count"], "sub_label": "{0} open"},
		{"key": "month", "label": "Sent this month", "tone": "ink",
		 "filters": [["docstatus", "=", 1], ["transaction_date", "Timespan", "this month"]], "metric": ["count"],
		 "sub": ["sum", "base_grand_total"], "sub_label": "{0}"},
		{"key": "won", "label": "Won", "tone": "ok", "filters": [["status", "=", "Ordered"]], "metric": ["count"],
		 "sub": ["sum", "base_grand_total"], "sub_label": "{0}"},
		{"key": "lost", "label": "Lost", "tone": "warn", "filters": [["status", "=", "Lost"]], "metric": ["count"]},
	],
	"Customer": [
		{"key": "total", "label": "Active customers", "tone": "ink", "filters": [["disabled", "=", 0]], "metric": ["count"]},
		{"key": "new", "label": "New this month", "tone": "ok", "filters": [["creation", "Timespan", "this month"]], "metric": ["count"]},
		{"key": "outstanding", "label": "With outstanding", "tone": "warn", "filters": [],
		 "metric": ["parties", "Sales Invoice", "customer"], "sub": ["party_sum", "Sales Invoice", "customer"], "sub_label": "{0} due"},
		{"key": "companies", "label": "Companies", "tone": "", "filters": [["customer_type", "=", "Company"]], "metric": ["count"]},
	],
	"Supplier": [
		{"key": "total", "label": "Active suppliers", "tone": "ink", "filters": [["disabled", "=", 0]], "metric": ["count"]},
		{"key": "new", "label": "New this month", "tone": "ok", "filters": [["creation", "Timespan", "this month"]], "metric": ["count"]},
		{"key": "outstanding", "label": "With payables", "tone": "warn", "filters": [],
		 "metric": ["parties", "Purchase Invoice", "supplier"], "sub": ["party_sum", "Purchase Invoice", "supplier"], "sub_label": "{0} due"},
		{"key": "on_hold", "label": "On hold", "tone": "", "filters": [["on_hold", "=", 1]], "metric": ["count"]},
	],
	"Item": [
		{"key": "active", "label": "Active items", "tone": "ink", "filters": [["disabled", "=", 0]], "metric": ["count"]},
		{"key": "stock", "label": "Stock items", "tone": "", "filters": [["disabled", "=", 0], ["is_stock_item", "=", 1]], "metric": ["count"]},
		{"key": "low", "label": "Low stock", "tone": "warn", "filters": [["disabled", "=", 0], ["is_stock_item", "=", 1]],
		 "metric": ["low_stock"], "sub_label": "below {0} units", "click": False},
		{"key": "value", "label": "Stock value", "tone": "ok", "filters": [], "metric": ["stock_value"], "click": False},
	],
	"Payment Entry": [
		{"key": "in", "label": "Received this month", "tone": "ok",
		 "filters": [["docstatus", "=", 1], ["payment_type", "=", "Receive"], ["posting_date", "Timespan", "this month"]],
		 "metric": ["sum", "base_received_amount"], "sub": ["count"], "sub_label": "{0} payments"},
		{"key": "out", "label": "Paid this month", "tone": "warn",
		 "filters": [["docstatus", "=", 1], ["payment_type", "=", "Pay"], ["posting_date", "Timespan", "this month"]],
		 "metric": ["sum", "base_paid_amount"], "sub": ["count"], "sub_label": "{0} payments"},
		{"key": "net", "label": "Net cash this month", "tone": "ink", "filters": [], "metric": ["net", "in", "out"], "click": False},
		DRAFTS,
	],
	"Journal Entry": [
		POSTED_MONTH("posting_date", "total_debit"),
		{"key": "bank", "label": "Bank entries", "tone": "ink",
		 "filters": [["docstatus", "=", 1], ["voucher_type", "=", "Bank Entry"], ["posting_date", "Timespan", "this month"]],
		 "metric": ["count"], "sub_label": "this month"},
		{"key": "opening", "label": "Opening entries", "tone": "", "filters": [["docstatus", "=", 1], ["is_opening", "=", "Yes"]], "metric": ["count"]},
		DRAFTS,
	],
	"Stock Entry": [
		POSTED_MONTH("posting_date", "total_amount", "Moved this month"),
		{"key": "receipt", "label": "Receipts", "tone": "ok", "filters": [["docstatus", "=", 1], ["purpose", "=", "Material Receipt"], ["posting_date", "Timespan", "this month"]], "metric": ["count"], "sub_label": "this month"},
		{"key": "issue", "label": "Issues", "tone": "warn", "filters": [["docstatus", "=", 1], ["purpose", "=", "Material Issue"], ["posting_date", "Timespan", "this month"]], "metric": ["count"], "sub_label": "this month"},
		{"key": "transfer", "label": "Transfers", "tone": "ink", "filters": [["docstatus", "=", 1], ["purpose", "=", "Material Transfer"], ["posting_date", "Timespan", "this month"]], "metric": ["count"], "sub_label": "this month"},
	],
	"Delivery Note": [
		POSTED_MONTH("posting_date", "base_grand_total", "Delivered this month"),
		{"key": "to_bill", "label": "To bill", "tone": "warn", "filters": [["docstatus", "=", 1], ["status", "=", "To Bill"]], "metric": ["count"], "sub": ["sum", "base_grand_total"], "sub_label": "{0}"},
		{"key": "completed", "label": "Completed", "tone": "ink", "filters": [["docstatus", "=", 1], ["status", "=", "Completed"]], "metric": ["count"]},
		DRAFTS,
	],
}

LOW_STOCK_UNITS = 10


@frappe.whitelist()
def get_config():
	"""Doctypes with cards, and each card's label/tone/click filters (for instant skeletons)."""
	out = {}
	for dt, cards in CONFIG.items():
		if not frappe.has_permission(dt, "read"):
			continue
		out[dt] = [
			{"key": c["key"], "label": _(c["label"]), "tone": c.get("tone", ""),
			 "filters": [f for f in c["filters"] if f[0] != "docstatus"] if c.get("click", True) else None}
			for c in cards
		]
	return out


def _resolve(filters):
	return [list(f) for f in filters]


def _merge(doctype, list_filters, card_filters):
	"""list filters AND card filters; on a field both filter, the card wins."""
	card_fields = {f[0] for f in card_filters}
	merged = []
	for f in list_filters or []:
		if isinstance(f, (list, tuple)) and len(f) >= 4:
			dt, field, op, val = f[0], f[1], f[2], f[3]
			if dt != doctype or field in card_fields:
				if dt == doctype:
					continue
			merged.append([dt, field, op, val])
	merged += [[doctype, *f] for f in card_filters]
	return merged


def _metric(doctype, metric, filters, company):
	kind = metric[0]
	if kind == "count":
		rows = frappe.get_list(doctype, fields=[{"COUNT": "*", "as": "n"}], filters=filters, limit_page_length=1)
		return {"value": rows[0].n if rows else 0, "fieldtype": "Int"}
	if kind == "sum":
		rows = frappe.get_list(doctype, fields=[{"SUM": metric[1], "as": "t"}], filters=filters, limit_page_length=1)
		return {"value": flt(rows[0].t) if rows else 0, "fieldtype": "Currency"}
	if kind in ("parties", "party_sum"):
		src, party = metric[1], metric[2]
		f = [[src, "docstatus", "=", 1], [src, "outstanding_amount", ">", 0]]
		if company:
			f.append([src, "company", "=", company])
		if not frappe.has_permission(src, "read"):
			return None
		if kind == "parties":
			rows = frappe.get_list(src, fields=[party], filters=f, group_by=party, limit_page_length=0)
			return {"value": len(rows), "fieldtype": "Int"}
		rows = frappe.get_list(src, fields=[{"SUM": "outstanding_amount", "as": "t"}], filters=f, limit_page_length=1)
		return {"value": flt(rows[0].t) if rows else 0, "fieldtype": "Currency"}
	if kind == "low_stock":
		if not frappe.has_permission("Bin", "read"):
			return None
		items = set(frappe.get_list("Item", filters=filters, pluck="name", limit_page_length=0))
		rows = frappe.get_list("Bin", fields=["item_code", {"SUM": "actual_qty", "as": "q"}],
			filters={"item_code": ["in", list(items) or [""]]}, group_by="item_code", limit_page_length=0)
		qty = {r.item_code: flt(r.q) for r in rows}
		return {"value": sum(1 for i in items if qty.get(i, 0) < LOW_STOCK_UNITS), "fieldtype": "Int", "sub_arg": LOW_STOCK_UNITS}
	if kind == "stock_value":
		from kodenova_theme.api.dashboard import stock_value
		if not frappe.has_permission("Bin", "read"):
			return None
		frappe.flags.kd_raw = True
		try:
			value = stock_value(json.dumps({"company": company}) if company else None)
		finally:
			frappe.flags.kd_raw = False
		return {"value": value, "fieldtype": "Currency"}
	return None


@frappe.whitelist()
def get_list_cards(doctype: str, filters: str | list | None = None):
	"""All cards for one list view in one call. Values respect the caller's permissions."""
	cards = CONFIG.get(doctype)
	if not cards or not frappe.has_permission(doctype, "read"):
		return None
	list_filters = frappe.parse_json(filters) or []
	meta = frappe.get_meta(doctype)
	company = None
	for f in list_filters:
		if isinstance(f, (list, tuple)) and len(f) >= 4 and f[1] == "company" and f[2] == "=":
			company = f[3]
	if not company:
		from kodenova_theme.api.dashboard import _company
		company = _company()
	currency = (frappe.get_cached_value("Company", company, "default_currency") if company else None) or frappe.db.get_default("currency")
	country = (frappe.get_cached_value("Company", company, "country") if company else None) or frappe.db.get_default("country")

	out, by_key = [], {}
	for c in cards:  # noqa: B007
		f = _merge(doctype, list_filters, _resolve(c["filters"]))
		if meta.has_field("company") and company and not any(x[1] == "company" for x in f):
			f.append([doctype, "company", "=", company])
		try:
			if c["metric"][0] == "net":
				a, b = by_key.get(c["metric"][1]), by_key.get(c["metric"][2])
				v = {"value": flt(a and a["value"]) - flt(b and b["value"]), "fieldtype": "Currency"}
			else:
				v = _metric(doctype, c["metric"], f, company)
			sub = _metric(doctype, c["sub"], f, company) if c.get("sub") and v is not None else None
		except frappe.PermissionError:
			frappe.clear_last_message()
			v, sub = None, None
		card = {"key": c["key"], "label": _(c["label"]), "tone": c.get("tone", ""), "currency": currency, "country": country,
				"value": v and v["value"], "fieldtype": v and v["fieldtype"],
				"sub": sub and sub["value"], "sub_fieldtype": sub and sub["fieldtype"],
				"sub_label": _sub_label(c.get("sub_label"), sub and sub["value"], sub and sub["fieldtype"]),
				"sub_arg": v and v.get("sub_arg"),
				"filters": [x for x in c["filters"] if x[0] != "docstatus"] if c.get("click", True) else None}
		by_key[c["key"]] = v
		out.append(card)
	return {"doctype": doctype, "company": company, "currency": currency, "country": country, "cards": out}


# Singular forms for count sub-labels ("1 payment", not "1 payments"). Translations for the singular
# use the context "one" (es/ar rows in translations/*.csv), so "1 abierta" / "فاتورة واحدة" read right.
SINGULAR = {"{0} invoices": "{0} invoice", "{0} orders": "{0} order", "{0} entries": "{0} entry", "{0} payments": "{0} payment"}


def _sub_label(raw, value=None, fieldtype=None):
	if not raw:
		return None
	if fieldtype in ("Int", None) and value is not None and flt(value) == 1:
		return _(SINGULAR.get(raw, raw), context="one")
	return _(raw)
