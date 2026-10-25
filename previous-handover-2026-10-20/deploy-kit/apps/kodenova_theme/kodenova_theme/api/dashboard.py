"""KodeERP dashboard chart sources.

Every number comes from frappe.get_list / get_all-with-permissions, so the reader's role and
user permissions apply (no raw SQL). Used by the Dashboard Chart Source records shipped in
kodenova_theme/kodenova_theme/dashboard_chart_source/.
"""

import frappe
from frappe import _
from frappe.utils import add_days, add_months, flt, get_first_day, get_last_day, getdate, nowdate
from frappe.utils.dashboard import cache_source


def _company(filters=None):
	"""Explicit filter > user default > the first company this user may see (a user restricted
	by User Permission to one company often has no default set). Never None while one exists,
	so figures are never summed across companies with different currencies."""
	filters = frappe.parse_json(filters) or {}
	if isinstance(filters, dict) and filters.get("company"):
		return filters["company"]
	company = frappe.defaults.get_user_default("Company")
	if company and frappe.has_permission("Company", "read", company):
		return company
	allowed = frappe.get_list("Company", pluck="name", order_by="creation asc", limit_page_length=1)
	return allowed[0] if allowed else company


def _sum(doctype, field, filters):
	rows = frappe.get_list(doctype, fields=[{"SUM": field, "as": "total"}], filters=filters, limit_page_length=1)
	return flt(rows[0].total) if rows else 0.0


def _months(n=6):
	today = getdate(nowdate())
	out = []
	for i in range(n - 1, -1, -1):
		start = get_first_day(add_months(today, -i))
		out.append((start, get_last_day(start)))
	return out


def _currency(company):
	return frappe.get_cached_value("Company", company, "default_currency") if company else None


LAKH_COUNTRIES = {"India", "Pakistan", "Bangladesh", "Nepal", "Sri Lanka"}


def compact_money(value, company=None):
	"""'Rs 7.94 L' / '$13.84 K' / '€1.2 M': symbol and abbreviation follow the COMPANY (its
	currency and country), not the site defaults, so a USD company on a PKR site reads right."""
	from frappe.utils import fmt_money

	currency = _currency(company) or frappe.db.get_default("currency")
	country = frappe.get_cached_value("Company", company, "country") if company else None
	units = [(1e7, _("Cr")), (1e5, _("L")), (1e3, _("K"))] if country in LAKH_COUNTRIES else [
		(1e9, _("B")), (1e6, _("M")), (1e3, _("K"))]
	value = flt(value)
	for size, label in units:
		if abs(value) >= size:
			return f"{fmt_money(round(value / size, 2), precision=2, currency=currency)} {label}"
	return fmt_money(value, precision=0, currency=currency)


@frappe.whitelist()
@cache_source
def sales_trend(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None,
				timespan=None, time_interval=None, heatmap_year=None):
	"""Net sales per month, last 6 months (submitted Sales Invoices)."""
	company = _company(filters)
	labels, values = [], []
	for start, end in _months(6):
		f = {"docstatus": 1, "posting_date": ["between", [start, end]]}
		if company:
			f["company"] = company
		labels.append(_(start.strftime("%b")))
		values.append(_sum("Sales Invoice", "base_net_total", f))
	# growth-chart style: soft bars + amber trend line over the same values (axis-mixed)
	return {
		"labels": labels,
		"datasets": [
			{"name": _("Net sales"), "values": values, "chartType": "bar"},
			{"name": _("Trend"), "values": values, "chartType": "line"},
		],
	}


@frappe.whitelist()
@cache_source
def receivables_ageing(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None,
				timespan=None, time_interval=None, heatmap_year=None):
	"""Outstanding Sales Invoice amounts bucketed by days past due."""
	company = _company(filters)
	today = getdate(nowdate())
	buckets = [
		(_("Current"), [">=", today]),
		("1-30", ["between", [add_days(today, -30), add_days(today, -1)]]),
		("31-60", ["between", [add_days(today, -60), add_days(today, -31)]]),
		("61-90", ["between", [add_days(today, -90), add_days(today, -61)]]),
		("90+", ["<", add_days(today, -90)]),
	]
	labels, values = [], []
	for label, cond in buckets:
		f = {"docstatus": 1, "outstanding_amount": [">", 0], "due_date": cond}
		if company:
			f["company"] = company
		labels.append(label)
		values.append(_sum("Sales Invoice", "outstanding_amount", f))
	return {"labels": labels, "datasets": [{"name": _("Outstanding"), "values": values}], "type": "bar"}


@frappe.whitelist()
@cache_source
def cash_flow(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None,
				timespan=None, time_interval=None, heatmap_year=None):
	"""Money received vs money paid per month, last 6 months (submitted Payment Entries)."""
	company = _company(filters)
	labels, cash_in, cash_out = [], [], []
	for start, end in _months(6):
		base = {"docstatus": 1, "posting_date": ["between", [start, end]]}
		if company:
			base["company"] = company
		labels.append(_(start.strftime("%b")))
		cash_in.append(_sum("Payment Entry", "base_received_amount", {**base, "payment_type": "Receive"}))
		cash_out.append(_sum("Payment Entry", "base_paid_amount", {**base, "payment_type": "Pay"}))
	return {
		"labels": labels,
		"datasets": [{"name": _("Cash in"), "values": cash_in}, {"name": _("Cash out"), "values": cash_out}],
		"type": "bar",
	}


@frappe.whitelist()
def stock_value(filters=None):
	"""Number card: value of stock on hand in the user's company, in the company's currency."""
	company = _company(filters)
	wh_filters = {"is_group": 0}
	if company:
		wh_filters["company"] = company
	warehouses = frappe.get_list("Warehouse", filters=wh_filters, pluck="name", limit_page_length=0)
	value = _sum("Bin", "stock_value", {"warehouse": ["in", warehouses]}) if warehouses else 0.0
	if frappe.flags.kd_raw:
		return value
	return compact_money(value, company)


# ---------------------------------------------------------------- money KPI number cards
# Money cards are "Custom" number cards so the symbol is the user's company currency (a
# Document Type card formats with the system currency, which is wrong for e.g. a USD company on
# a PKR site). Figures use frappe.get_list, so permissions apply. Click opens the filtered list.
THIS_MONTH = ("Timespan", "this month")
COUNT_KPIS = {
	"overdue_invoices": ("Sales Invoice", {"docstatus": 1, "status": "Overdue"}),
	"new_customers": ("Customer", {"creation": THIS_MONTH}),
	"open_quotations": ("Quotation", {"docstatus": 1, "status": ["in", ["Open", "Replied"]]}),
	"open_purchase_orders": ("Purchase Order", {"docstatus": 1, "status": ["in", ["To Receive and Bill", "To Bill", "To Receive"]]}),
	"overdue_bills": ("Purchase Invoice", {"docstatus": 1, "status": "Overdue"}),
	"active_stock_items": ("Item", {"disabled": 0, "is_stock_item": 1}),
	"deliveries_this_month": ("Delivery Note", {"docstatus": 1, "posting_date": THIS_MONTH}),
	"stock_entries_this_month": ("Stock Entry", {"docstatus": 1, "posting_date": THIS_MONTH}),
}
MONEY_KPIS = {
	"revenue_this_month": ("Sales Invoice", "base_net_total", {"docstatus": 1, "posting_date": THIS_MONTH}),
	"outstanding_receivables": ("Sales Invoice", "outstanding_amount", {"docstatus": 1, "outstanding_amount": (">", 0)}),
	"payables_due": ("Purchase Invoice", "outstanding_amount", {"docstatus": 1, "outstanding_amount": (">", 0)}),
	"cash_received_this_month": ("Payment Entry", "base_received_amount", {"docstatus": 1, "payment_type": "Receive", "posting_date": THIS_MONTH}),
	"purchases_this_month": ("Purchase Invoice", "base_net_total", {"docstatus": 1, "posting_date": THIS_MONTH}),
}


def _money_kpi(key, filters=None):
	doctype, field, flt_map = MONEY_KPIS[key]
	company = _company(filters)
	f = {k: list(v) if isinstance(v, tuple) else v for k, v in flt_map.items()}
	if company:
		f["company"] = company
	# a string is shown as-is by the number card widget (an object would be re-formatted with
	# the SITE currency and number system)
	return compact_money(_sum(doctype, field, f), company)


def _count_kpi(key, filters=None):
	doctype, flt_map = COUNT_KPIS[key]
	f = {k: list(v) if isinstance(v, tuple) else v for k, v in flt_map.items()}
	company = _company(filters)
	if company and frappe.get_meta(doctype).has_field("company"):
		f["company"] = company
	rows = frappe.get_list(doctype, fields=[{"COUNT": "*", "as": "n"}], filters=f, limit_page_length=1)
	return {
		"value": rows[0].n if rows else 0,
		"fieldtype": "Int",
		"route": ["List", doctype],
		"route_options": {k: v for k, v in f.items() if k != "docstatus"},
	}


def _make_kpi(key):
	def kpi(filters=None):
		return _money_kpi(key, filters) if key in MONEY_KPIS else _count_kpi(key, filters)

	kpi.__name__ = key
	return frappe.whitelist()(kpi)


for _key in [*MONEY_KPIS, *COUNT_KPIS]:
	globals()[_key] = _make_kpi(_key)
