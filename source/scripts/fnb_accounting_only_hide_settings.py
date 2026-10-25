# Hide "Settings" (Accounts Settings) in the Accounts sidebar for the non-admin fnb users (user layer).
import frappe, json
assert frappe.local.site == "fnb.localhost"
from frappe.desk.doctype.custom_sidebar.custom_sidebar import get_user_sidebar_layer, save_sidebar_customization
for u in frappe.get_all("User", filters={"module_profile": "KodeERP Accounting Only (F&B)"}, pluck="name"):
    frappe.set_user(u)
    rows = get_user_sidebar_layer("Accounts")
    for r in rows:
        if r.get("link_to") == "Accounts Settings": r["hidden"] = 1
    save_sidebar_customization("Accounts", json.dumps(rows))
    print("hid Settings for", u)
frappe.set_user("Administrator")
