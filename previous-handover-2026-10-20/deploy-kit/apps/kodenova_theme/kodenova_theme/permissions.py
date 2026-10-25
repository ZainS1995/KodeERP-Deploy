"""KodeERP privacy rules (hooks.permission_query_conditions / has_permission).

Non-admin desk users only see their own User record (demo users must not list other accounts).
System Managers and Administrator are unaffected.
"""
import frappe


def _is_admin(user):
	return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def user_query(user=None, doctype=None):
	user = user or frappe.session.user
	if _is_admin(user):
		return ""
	return f"`tabUser`.name = {frappe.db.escape(user)}"


def user_has_permission(doc, ptype=None, user=None, debug=False):
	user = user or frappe.session.user
	if _is_admin(user) or doc.name == user:
		return True
	# allow reading the minimal public info frappe needs for avatars/links, but not the record itself
	return False
