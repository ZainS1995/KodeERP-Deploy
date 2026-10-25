# Demo data: KDS sales tax -> Ecuador-style "IVA 15% (Demo)" (template + account renamed, rate 15%). Synthetic only.
import frappe
co = "Kodenova Demo Trading S.A. (Synthetic)"
old_acc, new_acc = "Sales Tax 12% - KDS", "IVA 15% - KDS"
if frappe.db.exists("Account", old_acc):
    frappe.rename_doc("Account", old_acc, new_acc, force=True)
    frappe.db.set_value("Account", new_acc, {"account_name": "IVA 15%", "tax_rate": 15})
old_t, new_t = "Sales Tax 12% (Demo) - KDS", "IVA 15% (Demo) - KDS"
if frappe.db.exists("Sales Taxes and Charges Template", old_t):
    frappe.rename_doc("Sales Taxes and Charges Template", old_t, new_t, force=True)
t = frappe.get_doc("Sales Taxes and Charges Template", new_t)
t.title = "IVA 15% (Demo)"; t.is_default = 1
for r in t.taxes: r.rate = 15; r.description = "IVA 15%"; r.account_head = new_acc
t.save(ignore_permissions=True); frappe.db.commit()
print(new_t, [(r.account_head, r.rate) for r in t.taxes])
