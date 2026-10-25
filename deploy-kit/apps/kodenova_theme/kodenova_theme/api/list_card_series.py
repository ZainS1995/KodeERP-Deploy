"""Mini charts for the list KPI cards (kodeerp_list_cards.js, v6).

Loaded in a second call after the cards have rendered, so the list never waits for charts.
Every figure comes from frappe.get_list (role permissions, user permissions and sharing apply);
nothing is invented: a card whose data cannot be read returns None and the client draws a flat
muted line. Results are cached per user + doctype + list filters for 2 minutes.

Per card, one of:
  {"kind": "line"|"bars", "months": ["2026-05", ...6], "points": [6 numbers], "fieldtype",
   "trend": % this month-to-date vs the same days of last month (or None), "basis"}
  {"kind": "ring"|"meter", "num": n, "den": d, "basis"}
"""

import hashlib
import json
from collections import OrderedDict

import frappe
from frappe.utils import add_months, cint, flt, get_first_day, get_last_day, getdate, nowdate

from kodenova_theme.api.list_cards import CONFIG, LOW_STOCK_UNITS, _merge, _resolve

MONTHS = 6
TTL = 120

# date field used to spread a status card (e.g. "Unpaid") over months
DATE_FIELD = {
	"Sales Invoice": "posting_date", "Purchase Invoice": "posting_date", "Payment Entry": "posting_date",
	"Journal Entry": "posting_date", "Stock Entry": "posting_date", "Delivery Note": "posting_date",
	"Sales Order": "transaction_date", "Purchase Order": "transaction_date", "Quotation": "transaction_date",
	"Customer": "creation", "Supplier": "creation", "Item": "creation",
}

# ratio cards: numerator = the card itself, denominator = these filters (same list context)
RATIO = {
	("Sales Invoice", "unpaid"): ("ring", {"metric": ["count"], "filters": [["docstatus", "=", 1], ["is_return", "=", 0]]}, "share of submitted invoices still unpaid", ["count"]),
	("Purchase Invoice", "unpaid"): ("ring", {"metric": ["count"], "filters": [["docstatus", "=", 1], ["is_return", "=", 0]]}, "share of submitted bills still unpaid", ["count"]),
	("Sales Invoice", "overdue"): ("ring", {"metric": ["sum", "outstanding_amount"], "filters": [["docstatus", "=", 1], ["outstanding_amount", ">", 0]]}, "overdue share of all outstanding"),
	("Purchase Invoice", "overdue"): ("ring", {"metric": ["sum", "outstanding_amount"], "filters": [["docstatus", "=", 1], ["outstanding_amount", ">", 0]]}, "overdue share of all outstanding"),
	("Item", "active"): ("ring", {"metric": ["count"], "filters": []}, "active share of all items"),
	("Item", "stock"): ("ring", {"metric": ["count"], "filters": [["disabled", "=", 0]]}, "stock items share of active items"),
	("Item", "low"): ("meter", {"metric": ["count"], "filters": [["disabled", "=", 0], ["is_stock_item", "=", 1]]}, "low-stock share of stock items"),
	("Customer", "outstanding"): ("ring", {"metric": ["count"], "filters": [["disabled", "=", 0]]}, "customers with a balance, of active customers"),
	("Customer", "companies"): ("ring", {"metric": ["count"], "filters": [["disabled", "=", 0]]}, "company customers, of active customers"),
	("Supplier", "outstanding"): ("ring", {"metric": ["count"], "filters": [["disabled", "=", 0]]}, "suppliers we owe, of active suppliers"),
	("Supplier", "on_hold"): ("ring", {"metric": ["count"], "filters": [["disabled", "=", 0]]}, "suppliers on hold, of active suppliers"),
	("Journal Entry", "opening"): ("ring", {"metric": ["count"], "filters": [["docstatus", "=", 1]]}, "opening entries, of submitted entries"),
}


CAPTION = {
	("Sales Invoice", "unpaid"): "of invoices",
	("Purchase Invoice", "unpaid"): "of bills",
	("Sales Invoice", "overdue"): "of outstanding",
	("Purchase Invoice", "overdue"): "of outstanding",
	("Item", "active"): "of all items",
	("Item", "stock"): "of active items",
	("Item", "low"): "of stock items",
	("Customer", "outstanding"): "of active customers",
	("Customer", "companies"): "of active customers",
	("Supplier", "outstanding"): "of active suppliers",
	("Supplier", "on_hold"): "of active suppliers",
	("Journal Entry", "opening"): "of submitted entries",
}


def _month_keys(today):
	first = get_first_day(today)
	return [add_months(first, -i) for i in range(MONTHS - 1, -1, -1)]


def _bucket(doctype, field, metric, filters, start, end):
	"""{YYYY-MM-DD(date): value} per day (or per row for datetime fields), one query."""
	is_dt = field in ("creation", "modified")
	window = [[doctype, field, ">=", str(start)], [doctype, field, "<=", str(end) + (" 23:59:59" if is_dt else "")]]
	f = [x for x in filters if x[1] != field] + window
	if metric[0] == "count":
		if is_dt:
			rows = frappe.get_list(doctype, fields=[field], filters=f, limit_page_length=20000)
			return [(getdate(r[field]), 1.0) for r in rows]
		rows = frappe.get_list(doctype, fields=[field, {"COUNT": "*", "as": "v"}], filters=f, group_by=field, limit_page_length=0)
	else:
		rows = frappe.get_list(doctype, fields=[field, {"SUM": metric[1], "as": "v"}], filters=f, group_by=field, limit_page_length=0)
	return [(getdate(r[field]), flt(r.v)) for r in rows]


def _scalar(doctype, metric, filters):
	if metric[0] == "count":
		rows = frappe.get_list(doctype, fields=[{"COUNT": "*", "as": "v"}], filters=filters, limit_page_length=1)
	else:
		rows = frappe.get_list(doctype, fields=[{"SUM": metric[1], "as": "v"}], filters=filters, limit_page_length=1)
	return flt(rows[0].v) if rows else 0.0


def _timespan_field(card):
	for f in card["filters"]:
		if len(f) == 3 and f[1] == "Timespan":
			return f[0]
	return None


def _monthly(doctype, field, metric, filters, today):
	months = _month_keys(today)
	start, end = months[0], get_last_day(today)
	pts = OrderedDict((m.strftime("%Y-%m"), 0.0) for m in months)
	mtd = prev = 0.0
	prev_start, prev_end = add_months(get_first_day(today), -1), add_months(today, -1)
	for d, v in _bucket(doctype, field, metric, filters, start, end):
		k = d.strftime("%Y-%m")
		if k in pts:
			pts[k] += v
		if get_first_day(today) <= d <= today:
			mtd += v
		if prev_start <= d <= prev_end:
			prev += v
	trend = round((mtd - prev) / prev * 100) if prev > 0 else None
	return list(pts.keys()), [round(v, 2) for v in pts.values()], trend


def _stock_value_series(company, today):
	"""Month-end stock value from the Stock Ledger (opening + monthly movements)."""
	if not frappe.has_permission("Stock Ledger Entry", "read"):
		return None
	months = _month_keys(today)
	base = [["Stock Ledger Entry", "is_cancelled", "=", 0]]
	if company:
		base.append(["Stock Ledger Entry", "company", "=", company])
	opening = _scalar("Stock Ledger Entry", ["sum", "stock_value_difference"], base + [["Stock Ledger Entry", "posting_date", "<", str(months[0])]])
	keys, moves, _t = _monthly("Stock Ledger Entry", "posting_date", ["sum", "stock_value_difference"], base, today)
	pts, run = [], opening
	for v in moves:
		run += v
		pts.append(round(run, 2))
	trend = round((pts[-1] - pts[-2]) / pts[-2] * 100) if len(pts) > 1 and pts[-2] > 0 else None
	return {"kind": "line", "months": keys, "points": pts, "fieldtype": "Currency", "trend": trend, "trend_basis": "vs last month-end",
			"basis": "month-end stock value (stock ledger)"}


def _series_for(doctype, card, list_filters, company, meta, today):
	f = _merge(doctype, list_filters, _resolve(card["filters"]))
	if meta.has_field("company") and company and not any(x[1] == "company" for x in f):
		f.append([doctype, "company", "=", company])
	metric = card["metric"]
	ratio = RATIO.get((doctype, card["key"]))
	if ratio:
		kind, den_spec, basis = ratio[:3]
		if len(ratio) > 3:
			metric = ratio[3]
		den_f = _merge(doctype, list_filters, _resolve(den_spec["filters"]))
		if meta.has_field("company") and company and not any(x[1] == "company" for x in den_f):
			den_f.append([doctype, "company", "=", company])
		den = _scalar(doctype, den_spec["metric"], den_f)
		if metric[0] in ("count", "sum"):
			num = _scalar(doctype, metric, f)
		elif metric[0] == "low_stock":
			from kodenova_theme.api.list_cards import _metric
			v = _metric(doctype, metric, f, company)
			num = flt(v and v["value"])
		elif metric[0] == "parties":
			from kodenova_theme.api.list_cards import _metric
			v = _metric(doctype, metric, f, company)
			num = flt(v and v["value"])
		else:
			return None
		return {"kind": kind, "num": num, "den": den, "basis": basis, "cap": CAPTION.get((doctype, card["key"]))}
	if metric[0] == "stock_value":
		return _stock_value_series(company, today)
	if metric[0] == "net":  # Payment Entry: received - paid per month
		cards = {c["key"]: c for c in CONFIG[doctype]}
		a, b = cards[metric[1]], cards[metric[2]]
		out = []
		for c in (a, b):
			field = _timespan_field(c)
			cf = _merge(doctype, list_filters, _resolve([x for x in c["filters"] if x[1] != "Timespan"]))
			if company:
				cf.append([doctype, "company", "=", company])
			out.append(_monthly(doctype, field, c["metric"], cf, today))
		keys = out[0][0]
		pts = [round(x - y, 2) for x, y in zip(out[0][1], out[1][1])]
		return {"kind": "bars", "months": keys, "points": pts, "fieldtype": "Currency", "trend": None, "basis": "received minus paid, per month"}
	if metric[0] not in ("count", "sum"):
		return None
	field = _timespan_field(card)
	if field:
		f = [x for x in f if not (x[1] == field and x[2] == "Timespan")]
		basis = "per month (" + field.replace("_", " ") + ")"
	else:
		field = DATE_FIELD.get(doctype, "creation")
		basis = "current matches, by " + field.replace("_", " ") + " month"
	keys, pts, trend = _monthly(doctype, field, metric, f, today)
	kind = "line" if metric[0] == "sum" else "bars"
	return {"kind": kind, "months": keys, "points": pts, "fieldtype": "Currency" if metric[0] == "sum" else "Int",
			"trend": trend if _timespan_field(card) else None, "trend_basis": "vs same days last month", "basis": basis}


@frappe.whitelist()
def get_list_card_series(doctype: str, filters: str | list | None = None):
	cards = CONFIG.get(doctype)
	if not cards or not frappe.has_permission(doctype, "read"):
		return None
	list_filters = frappe.parse_json(filters) or []
	key = "kd_card_series:" + hashlib.md5(json.dumps([frappe.session.user, doctype, list_filters, nowdate()], default=str).encode()).hexdigest()
	hit = frappe.cache.get_value(key)
	if hit:
		return hit
	company = None
	for f in list_filters:
		if isinstance(f, (list, tuple)) and len(f) >= 4 and f[1] == "company" and f[2] == "=":
			company = f[3]
	if not company:
		from kodenova_theme.api.dashboard import _company
		company = _company()
	meta = frappe.get_meta(doctype)
	today = getdate(nowdate())
	out = {}
	for c in cards:
		try:
			out[c["key"]] = _series_for(doctype, c, list_filters, company, meta, today)
		except frappe.PermissionError:
			frappe.clear_last_message()
			out[c["key"]] = None
		except Exception:
			frappe.log_error(title="KodeERP list card series", message=frappe.get_traceback())
			out[c["key"]] = None
	res = {"doctype": doctype, "series": out}
	frappe.cache.set_value(key, res, expires_in_sec=TTL)
	return res
