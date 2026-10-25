# Synthetic data cleanup: remove documents whose currency differs from their company currency (test runs),
# then spread demo customers' creation dates across Jul-Oct 2026.
import frappe, random
random.seed(11)
cos = {c.name: c.default_currency for c in frappe.get_all("Company", fields=["name", "default_currency"])}
DTS = ["Payment Entry", "Sales Invoice", "Delivery Note", "Sales Order", "Quotation", "Purchase Invoice", "Purchase Order", "Purchase Receipt"]
report = {}
for co, cur in cos.items():
    for dt in DTS:
        fld = "paid_from_account_currency" if dt == "Payment Entry" else "currency"
        bad = frappe.get_all(dt, filters={"company": co, fld: ["!=", cur], "docstatus": ["<", 2]}, pluck="name")
        if dt == "Payment Entry":  # receive into company-currency accounts only
            bad = [n for n in bad if frappe.db.get_value(dt, n, "paid_to_account_currency") != cur and frappe.db.get_value(dt, n, "paid_from_account_currency") != cur]
        for n in bad:
            report.setdefault(co, []).append(f"{dt} {n}")
# delete in dependency order (payments first)
for co, items in report.items():
    for dt in DTS:
        for it in [i for i in items if i.startswith(dt + " ")]:
            n = it[len(dt) + 1:]
            d = frappe.get_doc(dt, n)
            for pe in frappe.get_all("Payment Entry Reference", filters={"reference_name": n, "docstatus": 1}, pluck="parent"):
                p = frappe.get_doc("Payment Entry", pe); p.cancel(); frappe.delete_doc("Payment Entry", pe, force=1, ignore_permissions=True)
            if d.docstatus == 1: d.cancel()
            frappe.delete_doc(dt, n, force=1, ignore_permissions=True)
frappe.db.commit()
print("removed off-currency docs:", report or "none")
# currency check per company
for co, cur in cos.items():
    curs = set(frappe.get_all("Sales Invoice", filters={"company": co, "docstatus": 1}, pluck="currency")) | set(frappe.get_all("Purchase Invoice", filters={"company": co, "docstatus": 1}, pluck="currency"))
    print("currency", co, cur, sorted(curs))
# backdate synthetic customers/suppliers created today: first transaction date (or a random Jul-Oct date)
for dt, party_dt, field in (("Customer", "Sales Invoice", "customer"), ("Supplier", "Purchase Invoice", "supplier")):
    moved = 0
    for name in frappe.get_all(dt, filters={"creation": [">=", "2026-10-01"]}, pluck="name"):
        first = (frappe.get_all(party_dt, filters={field: name, "docstatus": 1}, fields=["posting_date"], order_by="posting_date asc", limit=1) or [{}])[0].get("posting_date")
        d = frappe.utils.add_days(first, -random.randint(3, 20)) if first else f"2026-{random.choice(['07','08','09'])}-{random.randint(1,28):02d}"
        d = max(frappe.utils.getdate(d), frappe.utils.getdate("2026-06-20"))
        frappe.db.sql(f"update `tab{dt}` set creation=%s, modified=%s where name=%s", (f"{d} 10:00:00", f"{d} 10:00:00", name)); moved += 1
    # a couple of genuinely new customers this month stays realistic
    print(dt, "backdated", moved)
for name in ["Hotel Río Guayas (Demo)", "فندق الواحة (تجريبي)"]:
    if frappe.db.exists("Customer", name):
        frappe.db.sql("update `tabCustomer` set creation='2026-10-06 10:00:00' where name=%s", name)
frappe.db.commit()
print("customers created in Oct 2026:", frappe.db.count("Customer", {"creation": [">=", "2026-10-01"]}), "of", frappe.db.count("Customer"))
