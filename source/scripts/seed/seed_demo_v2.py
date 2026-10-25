# Demo-story data (POS-equipment trader + café customer). Synthetic only.
#  KDS: USD, Guayaquil (Ecuador), "Sales Tax 12% (Demo)"  -> demo@ (en) and es.demo@ (es)
#  KSA: SAR, Riyadh (Saudi Arabia), VAT 15%, Arabic names  -> ar.demo@ (ar)
import random, frappe
from frappe.utils import getdate, add_days, add_months, nowdate
random.seed(77)
leaf = lambda dt: frappe.db.get_value(dt, {"is_group": 0}, "name")
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
CO = [
 dict(name="Kodenova Demo Trading S.A. (Synthetic)", abbr="KDS", country="Ecuador", cur="USD", users=["demo@kodeerp.test", "es.demo@kodeerp.test"],
      addr=dict(address_line1="Av. 9 de Octubre 100 (demo)", city="Guayaquil", country="Ecuador", phone="+593 4 000 0000"),
      tax=("Sales Tax 12%", 12, "Sales Tax 12% (Demo)"), pl_s="Venta USD (Sintético)", pl_b="Compra USD (Sintético)",
      custs=["Synthetic Cafe Theta (Demo)", "Café Malecón (Demo)", "Restaurante La Costa (Demo)", "Minimarket El Puerto (Demo)", "Farmacia Sana (Demo)", "Hotel Río Guayas (Demo)"],
      sups=["POS Supply Wholesale (Demo)", "Distribuidora Tecnológica del Pacífico (Demo)"],
      items=[("POS-PRN-80", "Impresora térmica 80 mm / Thermal printer (demo)", 120, 189), ("POS-SCN-2D", "Lector de códigos 2D / Barcode scanner (demo)", 55, 89),
             ("POS-PAP-80", "Rollo de papel térmico 80 mm / Paper roll (demo)", 0.6, 1.2), ("POS-TRM-15", "Terminal POS 15\" / POS terminal (demo)", 480, 749),
             ("POS-DRW-01", "Cajón de dinero / Cash drawer (demo)", 45, 79), ("POS-LAP-14", "Laptop 14\" / Laptop (demo)", 610, 899)]),
 dict(name="شركة كودنوفا للتجارة التجريبية (Demo)", abbr="KSA", country="Saudi Arabia", cur="SAR", users=["ar.demo@kodeerp.test"],
      addr=dict(address_line1="طريق الملك فهد 100 (تجريبي)", city="الرياض", country="Saudi Arabia", phone="+966 11 000 0000"),
      tax=("ضريبة القيمة المضافة 15%", 15, "ضريبة القيمة المضافة 15% (VAT)"), pl_s="بيع ريال (تجريبي)", pl_b="شراء ريال (تجريبي)",
      custs=["مقهى الياسمين (تجريبي)", "مطاعم البحر الأحمر (تجريبي)", "أسواق النخيل (تجريبي)", "صيدلية الشفاء (تجريبي)", "فندق الواحة (تجريبي)"],
      sups=["مورّد أنظمة نقاط البيع (تجريبي)", "شركة الأمل للإلكترونيات (تجريبي)"],
      items=[("AR-POS-PRN", "طابعة حرارية 80 مم (تجريبي)", 450, 709), ("AR-POS-SCN", "قارئ باركود ثنائي الأبعاد (تجريبي)", 205, 335),
             ("AR-POS-PAP", "لفة ورق حراري 80 مم (تجريبي)", 2.2, 4.5), ("AR-POS-TRM", "جهاز نقاط بيع 15 بوصة (تجريبي)", 1800, 2810),
             ("AR-POS-DRW", "درج نقود (تجريبي)", 170, 295), ("AR-POS-LAP", "حاسوب محمول 14 بوصة (تجريبي)", 2290, 3370)]),
]
out = {}
for c in CO:
    if not frappe.db.exists("Company", c["name"]):
        frappe.get_doc({"doctype": "Company", "company_name": c["name"], "abbr": c["abbr"], "default_currency": c["cur"], "country": c["country"],
                        "chart_of_accounts": "Standard", "create_chart_of_accounts_based_on": "Standard Template"}).insert(ignore_permissions=True)
        frappe.db.commit()
    co = c["name"]; ab = c["abbr"]; WH = f"Stores - {ab}"
    frappe.db.set_value("Currency", c["cur"], "enabled", 1)
    # address
    if not frappe.db.exists("Address", {"address_title": co}):
        a = frappe.get_doc({"doctype": "Address", "address_title": co, "address_type": "Billing", "is_your_company_address": 1, **c["addr"],
                            "links": [{"link_doctype": "Company", "link_name": co}]}); a.insert(ignore_permissions=True)
    # tax account + default template
    acc_name, rate, tpl = c["tax"]
    acc = f"{acc_name} - {ab}"
    if not frappe.db.exists("Account", acc):
        parent = frappe.db.get_value("Account", {"company": co, "account_name": "Duties and Taxes"}, "name")
        frappe.get_doc({"doctype": "Account", "account_name": acc_name, "company": co, "parent_account": parent, "account_type": "Tax", "tax_rate": rate}).insert(ignore_permissions=True)
    tpl_name = f"{tpl} - {ab}"
    if not frappe.db.exists("Sales Taxes and Charges Template", tpl_name):
        frappe.get_doc({"doctype": "Sales Taxes and Charges Template", "title": tpl, "company": co, "is_default": 1,
                        "taxes": [{"charge_type": "On Net Total", "account_head": acc, "rate": rate, "description": acc_name}]}).insert(ignore_permissions=True)
    taxes = get_taxes_and_charges("Sales Taxes and Charges Template", tpl_name)
    # price lists, parties, items, prices
    for pl, sell in ((c["pl_s"], 1), (c["pl_b"], 0)):
        if not frappe.db.exists("Price List", pl):
            frappe.get_doc({"doctype": "Price List", "price_list_name": pl, "currency": c["cur"], "selling": sell, "buying": 1 - sell, "enabled": 1}).insert(ignore_permissions=True)
    for n in c["custs"]:
        if not frappe.db.exists("Customer", n):
            frappe.get_doc({"doctype": "Customer", "customer_name": n, "customer_type": "Company", "customer_group": leaf("Customer Group"), "territory": leaf("Territory")}).insert(ignore_permissions=True)
        frappe.db.set_value("Customer", n, "default_price_list", c["pl_s"])
    for n in c["sups"]:
        if not frappe.db.exists("Supplier", n):
            frappe.get_doc({"doctype": "Supplier", "supplier_name": n, "supplier_group": leaf("Supplier Group"), "default_price_list": c["pl_b"]}).insert(ignore_permissions=True)
    for code, nm, cost, price in c["items"]:
        if not frappe.db.exists("Item", code):
            frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": nm, "item_group": leaf("Item Group"), "stock_uom": "Nos", "is_stock_item": 1, "valuation_rate": cost}).insert(ignore_permissions=True)
        for pl, v in ((c["pl_s"], price), (c["pl_b"], cost)):
            if not frappe.db.exists("Item Price", {"item_code": code, "price_list": pl}):
                frappe.get_doc({"doctype": "Item Price", "item_code": code, "price_list": pl, "price_list_rate": v}).insert(ignore_permissions=True)
    # users: default company via User Permission (replaces earlier company permissions)
    for u in c["users"]:
        for up in frappe.get_all("User Permission", filters={"user": u, "allow": "Company"}, pluck="name"):
            frappe.delete_doc("User Permission", up, ignore_permissions=True)
        frappe.get_doc({"doctype": "User Permission", "user": u, "allow": "Company", "for_value": co, "is_default": 1, "apply_to_all_doctypes": 1}).insert(ignore_permissions=True)
    frappe.db.commit()
    if frappe.db.count("Sales Invoice", {"company": co}):
        out[ab] = "already seeded"; continue
    ok = {"SE": 0, "PI": 0, "SI": 0, "PE": 0}; errs = []
    def pay(dt, name, d):
        pe = get_payment_entry(dt, name); pe.posting_date = str(d); pe.reference_no = "SYN-" + name; pe.reference_date = str(d)
        pe.insert(ignore_permissions=True); pe.submit(); ok["PE"] += 1
    today = getdate(nowdate()); m = getdate("2026-07-01"); ev = []
    while m <= today:
        ev += [(m, "SE"), (add_days(m, 5), "PI")] + [(add_days(m, random.randint(2, 27)), "SI") for _ in range(8)]
        m = add_months(m, 1)
    ev = sorted([e for e in ev if getdate(e[0]) <= today], key=lambda e: (getdate(e[0]), e[1] != "SE"))
    for d, k in ev:
        d = str(d)
        try:
            if k == "SE":
                se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": co, "posting_date": d, "set_posting_time": 1,
                    "items": [{"item_code": code, "qty": (400 if "PAP" in code else random.randint(20, 40)), "t_warehouse": WH, "basic_rate": cost} for code, nm, cost, p in c["items"]]})
                se.insert(ignore_permissions=True); se.submit()
            elif k == "PI":
                pi = frappe.get_doc({"doctype": "Purchase Invoice", "company": co, "supplier": random.choice(c["sups"]), "posting_date": d, "set_posting_time": 1, "bill_date": d,
                    "due_date": add_days(d, 30), "currency": c["cur"], "buying_price_list": c["pl_b"], "update_stock": 1, "set_warehouse": WH,
                    "items": [{"item_code": code, "qty": (200 if "PAP" in code else random.randint(5, 12)), "rate": cost, "warehouse": WH} for code, nm, cost, p in random.sample(c["items"], 3)]})
                pi.insert(ignore_permissions=True); pi.submit()
                if getdate(add_days(d, 10)) <= today: pay("Purchase Invoice", pi.name, add_days(d, 10))
            else:
                cust = c["custs"][0] if random.random() < 0.3 else random.choice(c["custs"])
                its = []
                for code, nm, cost, price in random.sample(c["items"], random.randint(2, 4)):
                    its.append({"item_code": code, "qty": (random.randint(20, 60) if "PAP" in code else random.randint(1, 4)), "rate": price, "warehouse": WH})
                si = frappe.get_doc({"doctype": "Sales Invoice", "company": co, "customer": cust, "posting_date": d, "set_posting_time": 1, "due_date": add_days(d, 30),
                    "currency": c["cur"], "selling_price_list": c["pl_s"], "update_stock": 1, "set_warehouse": WH, "taxes_and_charges": tpl_name, "taxes": taxes, "items": its})
                si.insert(ignore_permissions=True); si.submit()
                if random.random() < 0.55 and getdate(add_days(d, 12)) <= today: pay("Sales Invoice", si.name, add_days(d, 12))
            ok[k] += 1; frappe.db.commit()
        except Exception as e:
            frappe.db.rollback(); errs.append(f"{k} {d}: {str(e)[:200]}")
    out[ab] = {"created": ok, "n_err": len(errs), "errors": errs[:4],
               "overdue": frappe.db.count("Sales Invoice", {"company": co, "status": "Overdue"})}
print(out)
