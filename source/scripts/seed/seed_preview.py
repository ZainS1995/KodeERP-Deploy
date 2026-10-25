# Synthetic preview data (all names say Synthetic/Demo). Idempotent-ish: skips if marker supplier exists.
import random, frappe
from frappe.utils import getdate, add_days, add_months, nowdate
random.seed(42)
C = "Kodenova Demo Trading (Synthetic)"; ABBR = "KDT"; WH = f"Stores - {ABBR}"
if not frappe.db.exists("Fiscal Year", "2025-2026"):
    fy = frappe.get_doc({"doctype": "Fiscal Year", "year": "2025-2026", "year_start_date": "2025-07-01", "year_end_date": "2026-06-30"})
    fy.append("companies", {"company": C}); fy.insert()
grp = lambda dt, f: frappe.db.get_value(dt, {"is_group": 0}, "name")
sup_names = ["Synthetic Paper Mills (Demo)", "Synthetic Electronics Supply (Demo)", "Synthetic Packaging Co (Demo)", "Synthetic Office Depot (Demo)"]
for s in sup_names:
    if not frappe.db.exists("Supplier", s):
        frappe.get_doc({"doctype": "Supplier", "supplier_name": s, "supplier_group": grp("Supplier Group", 0)}).insert()
cust_new = ["Synthetic Pharma Epsilon (Demo)", "Synthetic Textiles Zeta (Demo)", "Synthetic Builders Eta (Demo)", "Synthetic Cafe Theta (Demo)", "Synthetic School Iota (Demo)", "Synthetic Clinic Kappa (Demo)"]
for c in cust_new:
    if not frappe.db.exists("Customer", c):
        frappe.get_doc({"doctype": "Customer", "customer_name": c, "customer_type": "Company", "customer_group": grp("Customer Group", 0), "territory": grp("Territory", 0)}).insert()
custs = frappe.get_all("Customer", pluck="name")
stock = [("SYN-STK-LAP", "Laptop 14in (synthetic)", 98000, 120000), ("SYN-STK-MON", "Monitor 24in (synthetic)", 28000, 36000),
         ("SYN-STK-KBD", "Keyboard (synthetic)", 2500, 3800), ("SYN-STK-MSE", "Mouse (synthetic)", 1200, 1900),
         ("SYN-STK-PRN", "Thermal printer (synthetic)", 18000, 24500), ("SYN-STK-SCN", "Barcode scanner (synthetic)", 6500, 9200),
         ("SYN-STK-PAP", "Receipt paper roll (synthetic)", 150, 260), ("SYN-STK-RTR", "Wi-Fi router (synthetic)", 7800, 11000)]
ig = grp("Item Group", 0)
for code, nm, cost, rate in stock:
    if not frappe.db.exists("Item", code):
        frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": nm, "item_group": ig, "stock_uom": "Nos", "is_stock_item": 1,
                        "valuation_rate": cost, "standard_rate": rate}).insert()
services = [("SYN-SVC-ERP", 45000), ("SYN-SVC-SUP", 12000), ("SYN-SVC-TRN", 8000)]
ok = {"SE": 0, "PI": 0, "SI": 0, "PE": 0}; errs = []
start = getdate("2026-05-01"); today = getdate(nowdate())
events = []
m = start
while m <= today:
    events.append((m, "SE")); events.append((add_days(m, 2), "PI")); events.append((add_days(m, 12), "PI"))
    for _ in range(7): events.append((add_days(m, random.randint(3, 27)), "SI"))
    m = add_months(m, 1)
events = sorted([e for e in events if getdate(e[0]) <= today], key=lambda e: (getdate(e[0]), e[1] != "SE"))
def run(kind, d):
    d = str(d)
    if kind == "SE":
        se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": C, "posting_date": d, "set_posting_time": 1,
                             "items": [{"item_code": c, "qty": random.randint(15, 40), "t_warehouse": WH, "basic_rate": cost} for c, n, cost, r in stock]})
        se.insert(); se.submit()
    elif kind == "PI":
        its = random.sample(stock, random.randint(2, 4))
        pi = frappe.get_doc({"doctype": "Purchase Invoice", "company": C, "supplier": random.choice(sup_names), "posting_date": d, "set_posting_time": 1,
                             "bill_date": d, "due_date": add_days(d, 30), "update_stock": 1, "set_warehouse": WH,
                             "items": [{"item_code": c, "qty": random.randint(5, 15), "rate": cost, "warehouse": WH} for c, n, cost, r in its]})
        pi.insert(); pi.submit()
        if random.random() < 0.7 and getdate(add_days(d, 10)) <= today: pay("Purchase Invoice", pi.name, add_days(d, 10))
    else:
        its = [{"item_code": c, "qty": random.randint(1, 4), "rate": r, "warehouse": WH} for c, n, cost, r in random.sample(stock, random.randint(1, 3))]
        if random.random() < 0.5:
            sc, sr = random.choice(services); its.append({"item_code": sc, "qty": 1, "rate": sr})
        si = frappe.get_doc({"doctype": "Sales Invoice", "company": C, "customer": random.choice(custs), "posting_date": d, "set_posting_time": 1,
                             "due_date": add_days(d, 30), "update_stock": 1, "set_warehouse": WH, "items": its})
        si.insert(); si.submit()
        if random.random() < 0.6 and getdate(add_days(d, 14)) <= today: pay("Sales Invoice", si.name, add_days(d, 14))
def pay(dt, name, d):
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry(dt, name); pe.posting_date = str(d); pe.reference_no = "SYN-" + name; pe.reference_date = str(d)
    pe.insert(); pe.submit(); ok["PE"] += 1
for d, kind in events:
    try:
        run(kind, d); ok[kind] += 1; frappe.db.commit()
    except Exception as e:
        frappe.db.rollback(); errs.append(f"{kind} {d}: {str(e)[:160]}")
print("created", ok); print("errors", len(errs)); print("\n".join(errs[:12]))
