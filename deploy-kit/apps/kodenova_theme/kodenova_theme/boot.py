"""KodeERP boot branding (hooks.extend_bootinfo).

Relabels the apps screen tiles and the rail logo with KodeERP equivalents by editing the boot
payload only. The underlying apps (ERPNext, Frappe HR, Frappe Framework) are unchanged and
credited on the single /licenses page (linked from About and the web footer) and in license files.
"""

IMG = "/assets/kodenova_theme/images/"
APP_BRANDING = {
	"erpnext": ("Intelliconz Accounting", IMG + "kodenova-app-erp.svg"),
	"hrms": ("Intelliconz People", IMG + "kodenova-app-hr.svg"),
	"frappe": ("Admin", IMG + "kodenova-app-admin.svg"),
	"kodenova_theme": ("Intelliconz Accounting Theme", IMG + "kodeerp-icon-192.png"),
}


def extend_bootinfo(bootinfo):
	for app in bootinfo.get("app_data") or []:
		brand = APP_BRANDING.get(app.get("app_name"))
		if brand:
			app["app_title"], app["app_logo_url"] = brand
	_hide_apps_with_no_visible_module(bootinfo)
	# The "updated to a new version" dialog renders upstream app titles/changelogs; suppress it.
	if bootinfo.get("change_log"):
		bootinfo["change_log"] = []


def _hide_apps_with_no_visible_module(bootinfo):
	"""Keep an app's tile off the apps screen when a Module Profile blocks every module of that app
	for this user (e.g. the F&B accounting profile blocks all HR modules, but HR/payroll is reached
	from the KodeERP sidebar, so the "KodeERP People" tile would lead to an empty area).
	Navigation only; permissions are untouched. Administrator is never affected."""
	import frappe
	from frappe.utils.modules import get_blocked_modules

	if frappe.session.user == "Administrator":
		return
	blocked = set(get_blocked_modules() or [])
	if not blocked:
		return
	for app in bootinfo.get("app_data") or []:
		if not app.get("on_apps_screen"):
			continue
		modules = frappe.get_all("Module Def", filters={"app_name": app.get("app_name")}, pluck="name")
		if modules and all(m in blocked for m in modules):
			app["on_apps_screen"] = False
