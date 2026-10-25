"""KodeERP branding: applies brand name, logo and favicon through supported settings DocTypes.

Idempotent; runs after install and after every migrate (hooks.after_install / after_migrate),
so `bench migrate` never resets the brand. Uses only public settings fields, no core patches.
"""

import frappe

BRAND_NAME = "KodeERP"
LOGO = "/assets/kodenova_theme/images/kodeerp-icon-192.png"  # official KodeERP K icon: desk sidebar / navbar (small)
LOCKUP = "/assets/kodenova_theme/images/kodeerp-logo.png"  # official KodeERP wordmark: login/update-password card and email masthead
FAVICON = "/assets/kodenova_theme/images/kodeerp-favicon.ico"
SPLASH = "/assets/kodenova_theme/images/kodeerp-icon-512.png"


def _set_single(doctype: str, values: dict) -> list[str]:
	changed = []
	meta = frappe.get_meta(doctype)
	for field, value in values.items():
		if not meta.has_field(field):
			continue
		if frappe.db.get_single_value(doctype, field) != value:
			frappe.db.set_single_value(doctype, field, value)
			changed.append(f"{doctype}.{field}")
	return changed


def apply_branding() -> list[str]:
	changed = []
	changed += _set_single("Website Settings", {"app_name": BRAND_NAME, "app_logo": LOCKUP, "favicon": FAVICON, "splash_image": SPLASH})
	changed += _set_single("Navbar Settings", {"app_logo": LOGO})
	changed += _set_single("System Settings", {"app_name": BRAND_NAME, "disable_standard_email_footer": 1})
	# email_body.get_footer reads the *default*, not the single; keep both in sync so the
	# upstream "Sent via ..." footer never reaches outgoing mail.
	if frappe.db.get_default("disable_standard_email_footer") != "1":
		frappe.db.set_default("disable_standard_email_footer", "1")
		changed.append("default.disable_standard_email_footer")
	if changed:
		frappe.clear_cache()
	return changed


PRINT_STYLE = "KodeERP"
LETTER_HEAD = "KodeERP Sandbox (Synthetic)"


def _read(rel: str) -> str:
	return open(frappe.get_app_path("kodenova_theme", *rel.split("/"))).read()


def apply_print_branding() -> list[str]:
	"""Print Style + default Letter Head (supported print DocTypes, sandbox data only)."""
	changed = []
	css = _read("print/kodeerp_print_style.css")
	if not frappe.db.exists("Print Style", PRINT_STYLE):
		frappe.get_doc({"doctype": "Print Style", "print_style_name": PRINT_STYLE, "css": css}).insert(ignore_permissions=True)
		changed.append("Print Style")
	elif frappe.db.get_value("Print Style", PRINT_STYLE, "css") != css:
		frappe.db.set_value("Print Style", PRINT_STYLE, "css", css)
		changed.append("Print Style.css")
	changed += _set_single("Print Settings", {"print_style": PRINT_STYLE, "font": "Default"})
	html = _read("print/letterhead.html")
	if not frappe.db.exists("Letter Head", LETTER_HEAD):
		frappe.get_doc({"doctype": "Letter Head", "letter_head_name": LETTER_HEAD, "source": "HTML",
			"content": html, "is_default": 1}).insert(ignore_permissions=True)
		changed.append("Letter Head")
	elif frappe.db.get_value("Letter Head", LETTER_HEAD, "content") != html:
		frappe.db.set_value("Letter Head", LETTER_HEAD, "content", html)
	return changed


def hide_vendor_onboarding_videos() -> int:
	"""Clear upstream (ERPNext/Frappe) YouTube intro videos on onboarding steps.

	The onboarding widget only renders media when intro_video_url is set, so this removes the
	vendor-branded thumbnails without touching core code. update_modified=False keeps the
	record's timestamp equal to the shipped JSON so migrate does not fight it; after_migrate
	re-applies it anyway.
	"""
	steps = frappe.get_all("Onboarding Step", filters={"intro_video_url": ["is", "set"]}, pluck="name")
	for name in steps:
		frappe.db.set_value("Onboarding Step", name, "intro_video_url", "", update_modified=False)
	return len(steps)


def apply_all() -> list[str]:
	changed = apply_branding()
	try:
		changed += apply_print_branding()
	except Exception:
		frappe.log_error("kodenova_theme: print branding failed")
	n = hide_vendor_onboarding_videos()
	if n:
		changed.append(f"onboarding videos cleared: {n}")
	from kodenova_theme.whitelabel import apply_whitelabel
	changed.append(f"whitelabel: {apply_whitelabel()}")
	frappe.clear_cache()
	return changed


def after_install():
	apply_all()


def after_migrate():
	apply_all()
