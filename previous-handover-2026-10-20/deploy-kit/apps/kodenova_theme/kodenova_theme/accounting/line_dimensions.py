"""Keep item and tax lines on the header's cost centre / accounting dimensions (KodeERP).

ERPNext only copies a header Cost Centre into *empty* item rows, and default tax rows get the
company's default cost centre (":Company" default). On a branch invoice that leaves income/expense
and VAT lines on Head Office while the header says Olaya, so P&L by cost centre and P&L by Branch
disagree. This hook (doc_events before_validate + validate) fills each item and tax line from the
header when the line is empty, or still on the company default while the header is a different
value. A line the user deliberately set to another non-default value is never touched.

Toggle: site_config ``kodeerp_sync_line_dimensions`` (default ON). Set it to 0 to disable:
    bench --site <site> set-config -p kodeerp_sync_line_dimensions 0

Header Cost Centre from Branch: when a document's Branch is set and its header Cost Centre is empty
or the company default, the header takes the branch's cost centre from the site mapping
``kodeerp_branch_cost_centers`` = {"<Company>": {"<Branch>": "<Cost Center>"}}; then the line sync
applies. A header Cost Centre deliberately set to another value is never changed.
Toggle: site_config ``kodeerp_branch_cost_center_sync`` (default ON).

Both rules are fail-safe: an unexpected error is written to Error Log and the save continues.
"""

import frappe

DOCTYPES = ("Sales Invoice", "Purchase Invoice", "POS Invoice", "Sales Order", "Delivery Note", "Purchase Order", "Purchase Receipt")
TABLES = ("items", "taxes")


def enabled():
	return bool(frappe.conf.get("kodeerp_sync_line_dimensions", 1))


def branch_cc_enabled():
	return bool(frappe.conf.get("kodeerp_branch_cost_center_sync", 1))


def branch_cost_centers(company):
	"""Valid {branch: cost centre} for the company from site_config (invalid entries ignored)."""
	raw = (frappe.conf.get("kodeerp_branch_cost_centers") or {}).get(company) or {}
	out = {}
	for br, cc in raw.items():
		if cc and frappe.get_cached_value("Cost Center", cc, "company") == company and not frappe.get_cached_value("Cost Center", cc, "is_group"):
			out[br] = cc
	return out


def header_cost_center(branch, current, default_cc, mapping):
	"""Header cost centre to set for this branch, or None to leave it alone (pure; unit tested)."""
	target = mapping.get(branch) if branch else None
	if not target or target == current:
		return None
	if not current or (default_cc and current == default_cc):
		return target
	return None


def pick(line_value, header_value, default_value):
	"""Value a line should carry, or None to leave it alone (pure; unit tested)."""
	if not header_value:
		return None
	if not line_value:
		return header_value
	if default_value and line_value == default_value and header_value != default_value:
		return header_value
	return None


def apply_to_rows(rows, header, defaults):
	"""rows: child docs; header: {field: header value}; defaults: {field: company default}. Returns changes."""
	changed = []
	for row in rows:
		for field, hval in header.items():
			if not hasattr(row, "meta") or row.meta.has_field(field):
				new = pick(row.get(field), hval, defaults.get(field))
				if new and new != row.get(field):
					changed.append((row.get("idx"), field, row.get(field), new))
					row.set(field, new)
	return changed


def _dimension_fields(company):
	"""{fieldname: company default} for cost_center and every enabled accounting dimension."""
	out = {"cost_center": frappe.get_cached_value("Company", company, "cost_center")}
	key = ("kodeerp_dims", company)
	cache = getattr(frappe.local, "kodeerp_dims_cache", None)
	if cache is None:
		cache = {}
		frappe.local.kodeerp_dims_cache = cache  # per request; Local has no __dict__
	if key not in cache:
		dims = {}
		for d in frappe.get_all("Accounting Dimension", filters={"disabled": 0}, fields=["name", "fieldname"]):
			dims[d.fieldname] = frappe.db.get_value(
				"Accounting Dimension Detail", {"parent": d.name, "company": company}, "default_dimension"
			)
		cache[key] = dims
	out.update(cache[key])
	return out


def _sync(doc):
	if doc.docstatus == 2 or not doc.get("company"):
		return
	defaults = _dimension_fields(doc.company)
	if branch_cc_enabled() and doc.meta.has_field("branch") and doc.meta.has_field("cost_center") and doc.get("branch"):
		new = header_cost_center(doc.branch, doc.get("cost_center"), defaults.get("cost_center"), branch_cost_centers(doc.company))
		if new:
			doc.cost_center = new
	if not enabled():
		return
	header = {f: doc.get(f) for f in defaults if doc.meta.has_field(f) and doc.get(f)}
	if not header:
		return
	for table in TABLES:
		if doc.meta.get_field(table):
			apply_to_rows(doc.get(table) or [], header, defaults)


def sync_line_dimensions(doc, method=None):
	try:
		_sync(doc)
	except Exception:
		# never block a save because of this convenience rule
		frappe.log_error(title="KodeERP line dimension sync", reference_doctype=doc.doctype, reference_name=doc.name)


@frappe.whitelist()
def client_config(company):
	"""Defaults the desk script needs to mirror the server rule live."""
	return {
		"enabled": enabled(),
		"branch_cc": branch_cc_enabled(),
		"defaults": _dimension_fields(company) if company else {},
		"branch_cost_centers": branch_cost_centers(company) if company else {},
	}
