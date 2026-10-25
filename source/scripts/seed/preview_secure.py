# Harden the site before public preview + create demo user. Passwords come from env (never stored in repo).
import os, frappe
from frappe.utils.password import update_password
update_password("Administrator", os.environ["ADMIN_PW"])
email = "demo@kodeerp.test"
if not frappe.db.exists("User", email):
    u = frappe.get_doc({"doctype": "User", "email": email, "first_name": "Demo", "last_name": "(Synthetic)",
                        "send_welcome_email": 0, "user_type": "System User", "language": "en"})
    u.insert(ignore_permissions=True)
u = frappe.get_doc("User", email)
want = ["Accounts User", "Sales User", "Purchase User", "Stock User", "Dashboard Manager"]
u.roles = [r for r in u.roles if r.role in want]
for r in want:
    if frappe.db.exists("Role", r) and r not in [x.role for x in u.roles]:
        u.append("roles", {"role": r})
u.enabled = 1
u.save(ignore_permissions=True)
update_password(email, os.environ["DEMO_PW"])
ws = frappe.get_single("Website Settings"); ws.disable_signup = 1; ws.save(ignore_permissions=True)
ss = frappe.get_single("System Settings")
ss.allow_consecutive_login_attempts = 5; ss.allow_login_after_fail = 120
ss.save(ignore_permissions=True)
print("roles", [r.role for r in frappe.get_doc("User", email).roles])
print("enabled system users", frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, pluck="name"))
from frappe.permissions import add_permission
add_permission("Accounting Dimension", "Accounts User", 0)  # Accounting workspace loads dimensions; read-only grant
