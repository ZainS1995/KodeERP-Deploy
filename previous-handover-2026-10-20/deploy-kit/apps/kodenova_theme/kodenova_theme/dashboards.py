"""KodeERP dashboards: default landing workspace + a no-migrate import helper.

Records themselves ship as app files (number_card/, dashboard_chart/, dashboard_chart_source/,
workspace/, sidebar/ under the "Kodenova Theme" module, plus fixtures/custom_html_block.json and
fixtures/custom_workspace.json). `bench migrate` imports all of them on its own.
"""

import glob
import os

import frappe

HOME_WORKSPACE = "KodeERP Home"


def apply_default_workspace(force: bool = False) -> int:
	"""Make KodeERP Home the landing page for every enabled desk user (keeps a user's own choice
	unless force=True). Suggested hook: after_migrate."""
	if not frappe.db.exists("Workspace", HOME_WORKSPACE):
		return 0
	filters = {"enabled": 1, "user_type": "System User", "name": ["not in", ["Guest"]]}
	if not force:
		filters["default_workspace"] = ["in", ["", None]]
	users = frappe.get_all("User", filters=filters, pluck="name")
	for user in users:
		frappe.db.set_value("User", user, "default_workspace", HOME_WORKSPACE, update_modified=False)
		frappe.cache.hdel("home_page", user)
	frappe.clear_cache()
	return len(users)


def set_default_workspace_for_new_user(doc, method=None):
	"""doc_events hook for User after_insert: new desk users land on KodeERP Home."""
	if doc.user_type == "System User" and not doc.default_workspace and frappe.db.exists("Workspace", HOME_WORKSPACE):
		frappe.db.set_value("User", doc.name, "default_workspace", HOME_WORKSPACE, update_modified=False)


def import_now():
	"""Import this app's dashboard files exactly as `bench migrate` would, without a full migrate.
	For the sandbox only: bench --site <site> execute kodenova_theme.dashboards.import_now"""
	from frappe.core.doctype.data_import.data_import import import_doc
	from frappe.modules.import_file import import_file_by_path

	module_path = frappe.get_app_path("kodenova_theme", "kodenova_theme")
	frappe.flags.in_import = True
	try:
		for folder in ("dashboard_chart_source", "number_card", "dashboard_chart"):
			for path in sorted(glob.glob(os.path.join(module_path, folder, "*", "*.json"))):
				import_file_by_path(path, force=True, ignore_version=True)
	finally:
		frappe.flags.in_import = False
	fixtures = frappe.get_app_path("kodenova_theme", "fixtures")
	import_doc(os.path.join(fixtures, "custom_html_block.json"))
	for folder in ("workspace", "sidebar"):
		for path in sorted(glob.glob(os.path.join(module_path, folder, "*", "*.json"))):
			import_file_by_path(path, force=True, ignore_version=True)
	import_doc(os.path.join(fixtures, "custom_workspace.json"))
	frappe.db.commit()
	n = apply_default_workspace()
	frappe.clear_cache()
	return n
