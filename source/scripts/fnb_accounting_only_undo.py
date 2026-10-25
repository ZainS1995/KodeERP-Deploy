# Undo fnb_accounting_only_apply.py + fnb_accounting_only_hide_settings.py on fnb.localhost. Run with:
#   cp scripts/fnb_accounting_only_undo.py docs/fnb-accounting-only/prestate.json development/ && \
#   sudo docker exec -u frappe kodeerp-frappe-1 /workspace/development/run_site_script.sh fnb.localhost /workspace/development/fnb_accounting_only_undo.py
import frappe, json, os
assert frappe.local.site == "fnb.localhost"
PROFILE = "KodeERP Accounting Only (F&B)"
p = "/workspace/development/prestate.json"
if not os.path.exists(p): p = "/workspace/development/fnb_accounting_only_prestate.json"
pre = json.load(open(p))
for u, st in pre["users"].items():
    d = frappe.get_doc("User", u); d.module_profile = st["module_profile"]
    d.set("block_modules", [{"module": m} for m in st["block_modules"]]); d.save(ignore_permissions=True)
    for n in frappe.get_all("Custom Sidebar", filters={"user": u, "module": "Accounts"}, pluck="name"): frappe.delete_doc("Custom Sidebar", n, ignore_permissions=True)
for m in ("Kodenova Theme", "Accounts"):
    for n in frappe.get_all("Custom Sidebar", filters={"module": m, "user": ["in", ["", None]]}, pluck="name"):
        if n not in pre["custom_sidebars"]: frappe.delete_doc("Custom Sidebar", n, ignore_permissions=True)
if frappe.db.exists("Module Profile", PROFILE): frappe.delete_doc("Module Profile", PROFILE, ignore_permissions=True)
frappe.db.set_value("Custom HTML Block", "KodeERP Quick Actions", "html", pre["quick_actions_html"])
for s in ["Purchases", "New purchase invoice", "Record a supplier bill with VAT.", "Input VAT tracked", "Branch cost centre", "Masters & POS"]:
    for n in frappe.get_all("Translation", filters={"source_text": s, "language": ["in", ["ar", "es"]]}, pluck="name"): frappe.delete_doc("Translation", n, ignore_permissions=True)
from frappe.translate import clear_cache; clear_cache(); frappe.clear_cache()
print("undone")
