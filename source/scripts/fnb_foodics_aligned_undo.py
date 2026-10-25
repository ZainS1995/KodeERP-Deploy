# Undo fnb_foodics_aligned_apply.py on fnb.localhost (returns to the "accounting only" state). Run with:
#   cp scripts/fnb_foodics_aligned_undo.py docs/fnb-foodics-aligned/fnb_foodics_prestate.json development/ && \
#   sudo docker exec -u frappe kodeerp-frappe-1 /workspace/development/run_site_script.sh fnb.localhost /workspace/development/fnb_foodics_aligned_undo.py
# Leaves posted/cancelled transactions alone. Masters still linked to cancelled test documents are disabled instead of deleted.
import frappe, json
from frappe.desk.doctype.custom_sidebar.custom_sidebar import save_site_sidebar
assert frappe.local.site == "fnb.localhost", "fnb only"
pre = json.load(open("/workspace/development/fnb_foodics_prestate.json"))
CO = "Najd Bites Food Co."
for u, roles in pre["roles"].items():
    d = frappe.get_doc("User", u); d.set("roles", [r for r in d.roles if r.role in roles]); d.save(ignore_permissions=True)
for dt in ("Bank Reconciliation Tool", "Opening Invoice Creation Tool", "BOM"):
    if not pre["custom_docperm"].get(dt): frappe.db.delete("Custom DocPerm", {"parent": dt})
save_site_sidebar("Kodenova Theme", json.dumps(pre["kodeerp_sidebar"]))
if pre.get("accounts_sidebar"): save_site_sidebar("Accounts", json.dumps(pre["accounts_sidebar"]))
for n in frappe.get_all("Custom Sidebar", filters={"module": "Kodenova Theme", "user": ["in", list(pre["roles"])]}, pluck="name"): frappe.delete_doc("Custom Sidebar", n, ignore_permissions=True)
frappe.db.set_value("Company", CO, "default_holiday_list", pre.get("company_holiday_list"))
frappe.db.set_value("Account", "Salaries Payable | الرواتب المستحقة - NJB", "account_type", pre.get("salaries_payable_type") or "")
b = frappe.get_doc("Salary Component", "Basic"); b.set("accounts", [a for a in b.accounts if a.company != CO]); b.save(ignore_permissions=True)
for bom in frappe.get_all("BOM", filters={"item": "MN-001", "docstatus": 1}, pluck="name"): frappe.get_doc("BOM", bom).cancel()
for dt, n in reversed(pre["created"]):
    if not frappe.db.exists(dt, n): continue
    try:
        d = frappe.get_doc(dt, n)
        if d.docstatus == 1: d.cancel()
        frappe.delete_doc(dt, n, ignore_permissions=True, force=dt in ("Workflow State", "Workflow Action Master")); frappe.db.commit(); print("deleted", dt, n)
    except Exception as e:
        frappe.db.rollback()
        meta = frappe.get_meta(dt)
        if meta.has_field("disabled"): frappe.db.set_value(dt, n, "disabled", 1)
        elif meta.has_field("is_active"): frappe.db.set_value(dt, n, "is_active", "No" if dt == "Salary Structure" else 0)
        frappe.db.commit(); print("kept (linked, disabled where possible)", dt, n, str(e)[:100])
for t in pre.get("translations_created", []):
    if frappe.db.exists("Translation", t): frappe.delete_doc("Translation", t, ignore_permissions=True)
frappe.clear_cache(); print("undone")
# Code: kodenova_theme/kodenova_theme/boot.py gained _hide_apps_with_no_visible_module (uncommitted); revert with
#   cd development/frappe-bench/apps/kodenova_theme && git checkout kodenova_theme/boot.py   (then HUP gunicorn)
