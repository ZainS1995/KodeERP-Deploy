# Synthetic: spread stock over 3 warehouses per demo company so "Stock Value by Warehouse" is meaningful.
import frappe, random
random.seed(5)
from frappe.utils import nowdate
SETS = {"KDS": ("Kodenova Demo Trading S.A. (Synthetic)", ["Showroom Guayaquil", "Bodega Quito"], "POS-"),
        "KSA": ("شركة كودنوفا للتجارة التجريبية (Demo)", ["صالة العرض الرياض", "مستودع جدة"], "AR-POS-")}
for ab, (co, whs, pre) in SETS.items():
    parent = frappe.db.get_value("Warehouse", {"company": co, "is_group": 1}, "name")
    src = f"Stores - {ab}"
    for w in whs:
        name = f"{w} - {ab}"
        if not frappe.db.exists("Warehouse", name):
            frappe.get_doc({"doctype": "Warehouse", "warehouse_name": w, "company": co, "parent_warehouse": parent}).insert(ignore_permissions=True)
        if frappe.db.exists("Stock Entry", {"company": co, "stock_entry_type": "Material Transfer", "docstatus": 1, "remarks": f"SYN transfer {name}"}):
            continue
        items = []
        for b in frappe.get_all("Bin", filters={"warehouse": src, "actual_qty": [">", 4], "item_code": ["like", pre + "%"]}, fields=["item_code", "actual_qty"]):
            q = int(b.actual_qty * random.uniform(0.2, 0.35))
            if q > 0: items.append({"item_code": b.item_code, "qty": q, "s_warehouse": src, "t_warehouse": name})
        if items:
            se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Transfer", "company": co, "posting_date": "2026-10-05", "set_posting_time": 1,
                                 "remarks": f"SYN transfer {name}", "items": items}); se.insert(ignore_permissions=True); se.submit()
            print(ab, name, len(items))
frappe.db.set_value("Report", "Stock Balance", "prepared_report", 0)
frappe.db.commit()
