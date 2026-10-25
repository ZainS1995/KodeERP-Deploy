import random
from frappe.utils import add_days, nowdate
random.seed(7)
company = "Kodenova Demo Trading (Synthetic)"
custs = ["Synthetic Customer Alpha","Synthetic Retail Beta (Demo)","Synthetic Logistics Gamma (Demo)","Synthetic Foods Delta (Demo)"]
for c in custs:
    if not frappe.db.exists("Customer", c):
        frappe.get_doc({"doctype":"Customer","customer_name":c,"customer_type":"Company","customer_group":frappe.db.get_value("Customer Group",{"is_group":0}) ,"territory":frappe.db.get_value("Territory",{"is_group":0})}).insert()
items = [("SYN-SVC-ERP","ERP implementation (synthetic)",45000),("SYN-SVC-SUP","Monthly support plan (synthetic)",12000),("SYN-SVC-TRN","User training day (synthetic)",8000)]
for code,nm,rate in items:
    if not frappe.db.exists("Item", code):
        frappe.get_doc({"doctype":"Item","item_code":code,"item_name":nm,"item_group":frappe.db.get_value("Item Group",{"is_group":0}),"stock_uom":"Nos","is_stock_item":0,"standard_rate":rate}).insert()
if frappe.db.count("Sales Invoice") == 0:
    for i in range(9):
        d = add_days(nowdate(), -random.randint(0, 105))
        si = frappe.get_doc({"doctype":"Sales Invoice","company":company,"customer":random.choice(custs),"posting_date":d,"set_posting_time":1,"due_date":add_days(d,30),
            "items":[{"item_code":code,"qty":random.randint(1,4),"rate":rate} for code,nm,rate in random.sample(items, random.randint(1,3))]})
        si.insert()
        if i < 7: si.submit()
print("SI", frappe.get_all("Sales Invoice", fields=["name","customer","grand_total","status","posting_date"]))
