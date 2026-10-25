import os
from frappe.utils.password import update_password
pw = open("/workspace/development/.rtl_pw").read().strip()
e = "rtl.test@example.com"
if not frappe.db.exists("User", e):
    u = frappe.get_doc({"doctype":"User","email":e,"first_name":"RTL","last_name":"Test (Synthetic)","language":"ar","send_welcome_email":0,"user_type":"System User"})
    u.insert(); u.add_roles("System Manager","Accounts Manager","Accounts User")
update_password(e, pw)
print("ok", frappe.db.get_value("User", e, "language"))
