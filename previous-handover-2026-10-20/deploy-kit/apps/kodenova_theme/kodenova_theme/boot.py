"""KodeERP boot branding (hooks.extend_bootinfo).

Relabels the apps screen tiles and the rail logo with KodeERP equivalents by editing the boot
payload only. The underlying apps (ERPNext, Frappe HR, Frappe Framework) are unchanged and
credited on the single /licenses page (linked from About and the web footer) and in license files.
"""

IMG = "/assets/kodenova_theme/images/"
APP_BRANDING = {
	"erpnext": ("KodeERP", IMG + "kodenova-app-erp.svg"),
	"hrms": ("KodeERP People", IMG + "kodenova-app-hr.svg"),
	"frappe": ("Admin", IMG + "kodenova-app-admin.svg"),
	"kodenova_theme": ("KodeERP Theme", IMG + "kodeerp-icon-192.png"),
}


def extend_bootinfo(bootinfo):
	for app in bootinfo.get("app_data") or []:
		brand = APP_BRANDING.get(app.get("app_name"))
		if brand:
			app["app_title"], app["app_logo_url"] = brand
	# The "updated to a new version" dialog renders upstream app titles/changelogs; suppress it.
	if bootinfo.get("change_log"):
		bootinfo["change_log"] = []
