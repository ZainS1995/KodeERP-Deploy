# Synthetic default bank ledger so the Bank Balance dashboard chart renders (no real bank data).
import frappe
for company, abbr in frappe.get_all("Company", fields=["name", "abbr"], as_list=True):
    if frappe.db.get_value("Company", company, "default_bank_account"):
        continue
    parent = frappe.db.get_value("Account", {"company": company, "account_type": "Bank", "is_group": 1}, "name") or \
             frappe.db.get_value("Account", {"company": company, "account_name": "Bank Accounts", "is_group": 1}, "name")
    name = f"Synthetic Demo Bank - {abbr}"
    if not frappe.db.exists("Account", name):
        frappe.get_doc({"doctype": "Account", "account_name": "Synthetic Demo Bank", "company": company, "parent_account": parent,
                        "account_type": "Bank", "is_group": 0}).insert(ignore_permissions=True)
    frappe.db.set_value("Company", company, "default_bank_account", name)
    print(company, "->", name)
