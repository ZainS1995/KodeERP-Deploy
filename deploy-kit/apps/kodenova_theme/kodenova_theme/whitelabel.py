"""KodeERP white-label layer (v0.5). Runs from after_migrate via branding.apply_all().

Only touches records through supported DocTypes/settings (Navbar Settings, System Settings,
Workspace/Onboarding/Report records, Number Card, Dashboard Chart). Upstream source files are
never modified. Idempotent: safe to run on every migrate.
"""
import json
import re

import frappe

NAMES = [("Frappe Framework", "Intelliconz Platform"), ("Frappe HR", "Intelliconz People"), ("Frappe CRM", "Intelliconz CRM"),
	("Frappe Cloud", "Intelliconz Cloud"), ("ERPNext", "Intelliconz Accounting"), ("Frappe", "Intelliconz Accounting")]
DOC_LINK = re.compile(r"\s*See \[[^\]]+\]\(https?://[^)]*(frappe|erpnext)[^)]*\)\.?", re.I)
ANY_LINK = re.compile(r"\[([^\]]+)\]\(https?://[^)]*(frappe\.io|erpnext\.com|frappeframework\.com)[^)]*\)", re.I)
BRAND_URL = re.compile(r"(frappe\.io|erpnext\.com|frappeframework\.com|frappe\.cloud|frappecloud\.com|github\.com/frappe)", re.I)


def rebrand_text(s):
	if not s or not isinstance(s, str):
		return s
	s = DOC_LINK.sub("", s)
	s = ANY_LINK.sub(r"\1", s)
	for a, b in NAMES:
		s = s.replace(a, b)
	return s


def _rebrand_records(doctype, fields, url_fields=()):
	n = 0
	if not frappe.db.exists("DocType", doctype):
		return 0
	meta = frappe.get_meta(doctype)
	fields = [f for f in fields if meta.has_field(f)]
	url_fields = [f for f in url_fields if meta.has_field(f)]
	for r in frappe.get_all(doctype, fields=["name", *fields, *url_fields], limit=0):
		upd = {}
		for f in fields:
			new = rebrand_text(r.get(f))
			if new != r.get(f):
				upd[f] = new
		for f in url_fields:
			if r.get(f) and BRAND_URL.search(r.get(f)):
				upd[f] = ""
		if upd:
			frappe.db.set_value(doctype, r.name, upd, update_modified=False)
			n += 1
	return n


def rebrand_records():
	out = {}
	out["Onboarding Step"] = _rebrand_records("Onboarding Step", ["title", "description", "action_label", "intro_video_url"], ["path", "video_url"])
	out["Module Onboarding"] = _rebrand_records("Module Onboarding", ["title", "subtitle", "success_message"], ["documentation_url"])
	out["Form Tour Step"] = _rebrand_records("Form Tour Step", ["title", "description"])
	out["Report"] = _rebrand_records("Report", [], ["documentation_url"])
	out["Workspace"] = _rebrand_records("Workspace", ["label", "title"])
	out["Workspace Link"] = _rebrand_records("Workspace Link", ["label"])
	out["Workspace Shortcut"] = _rebrand_records("Workspace Shortcut", ["label"])
	return out


def navbar_and_email():
	changed = []
	ns = frappe.get_single("Navbar Settings")
	dirty = False
	# Remove upstream vendor items (e.g. "Frappe Support" -> frappe.io) from the help menu entirely.
	vendor = [r for r in ns.help_dropdown if (r.route and BRAND_URL.search(r.route)) or (r.item_label and re.search("Frappe|ERPNext", r.item_label))]
	if vendor:
		ns.set("help_dropdown", [r for r in ns.help_dropdown if r not in vendor])
		dirty = True
	# Licenses stay discreet: linked only from the About dialog and the web footer, not the help menu.
	keep = [r for r in ns.help_dropdown if (r.route or "") != "/licenses"]
	if len(keep) != len(ns.help_dropdown):
		ns.set("help_dropdown", keep)
		dirty = True
	# Language switcher in the user (settings) menu, available to every user.
	if not any((r.action or "") == "kodeerp.switch_language()" for r in ns.settings_dropdown):
		ns.append("settings_dropdown", {"item_label": "Language", "item_type": "Action", "action": "kodeerp.switch_language()"})
		dirty = True
	if dirty:
		ns.save(ignore_permissions=True)
		changed.append("Navbar Settings.help_dropdown")
	footer = "Intelliconz Accounting"
	if frappe.db.get_default("email_footer_address") != footer:
		frappe.db.set_default("email_footer_address", footer)
		changed.append("email_footer_address")
	if not frappe.db.get_single_value("System Settings", "disable_standard_email_footer"):
		frappe.db.set_single_value("System Settings", "disable_standard_email_footer", 1)
		changed.append("System Settings.disable_standard_email_footer")
	return changed


def hide_doctype_doc_links():
	"""Upstream DocTypes link 'Documentation' to docs.frappe.io / erpnext.com in list/form sidebars.
	Blank them with Property Setters (the supported customization layer)."""
	from frappe.custom.doctype.property_setter.property_setter import make_property_setter

	n = 0
	for dt in frappe.get_all("DocType", filters={"documentation": ["is", "set"]}, fields=["name", "documentation"], limit=0):
		if not BRAND_URL.search(dt.documentation or ""):
			continue
		if frappe.db.get_value("Property Setter", {"doc_type": dt.name, "property": "documentation", "doctype_or_field": "DocType"}, "value") == "":
			continue
		make_property_setter(dt.name, None, "documentation", "", "Data", for_doctype=True, validate_fields_for_doctype=False)
		n += 1
	return n


HTML_DOC_LINK = re.compile(r'<a\b[^>]*href=["\']?[^"\'>]*(frappe\.io|erpnext\.com|frappeframework\.com)[^>]*>(.*?)</a>', re.I | re.S)


def strip_doc_links(text):
	"""Remove upstream documentation links from help text: 'View Documentation'-style anchors are
	dropped, other anchors keep their text. Markdown links are handled by rebrand_text()."""
	if not text:
		return text
	def _sub(m):
		inner = re.sub(r"<[^>]+>", "", m.group(2)).strip()
		return "" if re.search(r"documentation|docs|learn more|read more|click here", inner, re.I) else inner
	out = HTML_DOC_LINK.sub(_sub, text)
	out = rebrand_text(out)
	out = re.sub(r"https?://\S*(frappe\.io|erpnext\.com)\S*", "", out)
	return re.sub(r"\(\s*\)|\s{2,}", " ", out).strip()


def override_field_descriptions():
	"""Property Setters for every DocField / Custom Field description that links to upstream docs."""
	from frappe.custom.doctype.property_setter.property_setter import make_property_setter

	n = 0
	rows = frappe.db.sql(
		"""select parent, fieldname, description from `tabDocField`
		where description regexp 'frappe\\.io|erpnext\\.com|frappeframework\\.com|ERPNext|Frappe'""", as_dict=True)
	for r in rows:
		new = strip_doc_links(r.description)
		if new == r.description:
			continue
		cur = frappe.db.get_value("Property Setter", {"doc_type": r.parent, "field_name": r.fieldname, "property": "description"}, "value")
		if cur == new:
			continue
		make_property_setter(r.parent, r.fieldname, "description", new, "Small Text", validate_fields_for_doctype=False)
		n += 1
	return n


def demo_report_settings():
	"""Stock Balance runs live (not as a queued 'prepared report') so demo users see rows immediately.
	Small SaaS tenants don't need the background-prepared mode; re-applied after every migrate."""
	n = 0
	for r in ("Stock Balance",):
		if frappe.db.get_value("Report", r, "prepared_report"):
			frappe.db.set_value("Report", r, "prepared_report", 0); n += 1
	return n


def apply_whitelabel():
	# The KodeERP Home dashboard (workspace, number cards, charts) is owned by a separate module/worker.
	return {"records": rebrand_records(), "settings": navbar_and_email(), "doctype_doc_links": hide_doctype_doc_links(),
		"reports_live": demo_report_settings()}
	# Field descriptions are cleaned client-side (kodenova_theme.js) so that es/ar translations of the
	# upstream text keep matching; override_field_descriptions() is kept for English-only sites.
