"""Sales-only menu for one user (navigation only; permissions are NOT changed).

The user sees: Dashboard, Sales (Sales Invoice, Credit Note, Customers), Reports, Settings.
Everything else is hidden in that user's own sidebar layer. Other users and Administrator are untouched.
Typing a URL such as /desk/journal-entry still opens the page if the user has the role for it.

Run inside the backend container, from the bench's sites folder:
    docker compose cp sales_only_menu.py backend:/tmp/sales_only_menu.py
    docker compose exec -T backend bash -c "cd /home/frappe/frappe-bench/sites && ../env/bin/python /tmp/sales_only_menu.py <site> <user> dry"
    ... same with `apply`, and later `undo`.
`dry` prints the resulting menu and changes nothing. `undo` deletes this user's sidebar layers (the user then sees the site menu again).
Afterwards: bench --site <site> clear-cache, then reload the browser (Ctrl+F5).
"""
import json
import sys

import frappe
from frappe.desk.doctype.custom_sidebar.custom_sidebar import _save_customization, layer_arrangement

MODULES = ("Kodenova Theme", "Accounts")
REPORTS = ["Sales Register", "Accounts Receivable", "Customer Ledger Summary"]
SETTINGS = [("Company", "DocType", "Company", "building"), ("Accounts Settings", "DocType", "Accounts Settings", "settings"),
            ("Print Settings", "DocType", "Print Settings", "printer")]


def section(label, icon):
    return {"type": "Section Break", "label": label, "icon": icon, "collapsible": 1, "child": 0, "added": 1}


def link(label, link_type, link_to, icon):
    return {"type": "Link", "label": label, "link_type": link_type, "link_to": link_to, "icon": icon,
            "child": 1, "collapsible": 1, "added": 1, "hidden": 0}


def build_menu(user):
    old = layer_arrangement("Kodenova Theme", user)
    by_to = {}
    for r in old:
        if r.get("link_to") and r["link_to"] not in by_to:
            by_to[r["link_to"]] = dict(r)

    def existing(to, label, link_type, icon):
        r = by_to.get(to)
        if r:
            r.update({"hidden": 0, "child": 1, "label": label})
            return r
        return link(label, link_type, to, icon)

    home = by_to.get("KodeERP Home") or link("Home", "Workspace", "KodeERP Home", "house")
    home.update({"hidden": 0, "child": 0, "label": "Dashboard"})
    menu = [home, section("Sales", "receipt-text"),
            existing("Sales Invoice", "Sales Invoice", "DocType", "receipt-text"),
            # a credit note is a Sales Invoice with "Is Return" ticked
            link("Return / Credit Note", "URL", "/desk/sales-invoice?is_return=1", "undo-2"),
            existing("Customer", "Customers", "DocType", "user-round")]
    reports = [link(n, "Report", n, "chart-column") for n in REPORTS if frappe.db.exists("Report", n)]
    if reports:
        menu += [section("Reports", "chart-column")] + reports
    menu += [section("Settings", "settings")] + [link(*s) for s in SETTINGS if frappe.db.exists("DocType", s[2])]
    used = {(r.get("type"), r.get("link_to") or r.get("label")) for r in menu}
    # every other row of the user's current menu stays in the list, hidden
    for r in old:
        if (r.get("type"), r.get("link_to") or r.get("label")) in used:
            continue
        menu.append(dict(r, hidden=1))
    return menu


def main(site, user, mode):
    frappe.init(site=site, sites_path=".")
    frappe.connect()
    try:
        if not frappe.db.exists("User", user):
            sys.exit(f"user {user} not found")
        if mode == "undo":
            for m in MODULES:
                for n in frappe.get_all("Custom Sidebar", filters={"user": user, "module": m}, pluck="name"):
                    frappe.delete_doc("Custom Sidebar", n, ignore_permissions=True)
            frappe.db.commit()
            frappe.clear_cache()
            print("undone for", user)
            return
        menu = build_menu(user)
        print("Visible menu for", user)
        for r in menu:
            if not r.get("hidden"):
                print("  " + ("  " if r.get("child") else "") + str(r.get("label")), "->", r.get("link_to") or "")
        print("hidden rows:", sum(1 for r in menu if r.get("hidden")))
        if mode != "apply":
            print("DRY RUN: nothing saved. Re-run with `apply`.")
            return
        _save_customization("Kodenova Theme", json.dumps(menu), user=user)
        # second sidebar (Accounts): hide every row so the sidebar switcher does not bring the old menu back
        acc = [dict(r, hidden=1) for r in layer_arrangement("Accounts", user)]
        if acc:
            _save_customization("Accounts", json.dumps(acc), user=user)
        frappe.db.commit()
        frappe.clear_cache()
        print("applied for", user)
    finally:
        frappe.destroy()


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[3] not in ("dry", "apply", "undo"):
        sys.exit("usage: sales_only_menu.py <site> <user> dry|apply|undo")
    main(*sys.argv[1:])
