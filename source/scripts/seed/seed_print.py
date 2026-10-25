# Sandbox print setup: KodeERP letter head as company default + Standard print format for Sales Invoice.
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
lh = "KodeERP Sandbox (Synthetic)"
print("company lh before", frappe.get_all("Company", fields=["name","default_letter_head"]))
for c in frappe.get_all("Company", pluck="name"):
    frappe.db.set_value("Company", c, "default_letter_head", lh)
make_property_setter("Sales Invoice", None, "default_print_format", "Standard", "Data", for_doctype=True)
print("letterheads", frappe.get_all("Letter Head", fields=["name","is_default"]))
for n in frappe.get_all("Sales Invoice", pluck="name"):
    frappe.db.set_value("Sales Invoice", n, "letter_head", "KodeERP Sandbox (Synthetic)", update_modified=False)
print("ok")
