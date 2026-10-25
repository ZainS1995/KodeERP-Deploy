# Synthetic multilingual demo: LatAm USD distributor (es) + Saudi SAR trader (ar) with data, demo users,
# and per-user default company. All names are clearly marked Demo / Sintético / تجريبي. Passwords from env.
import os, random, frappe
from frappe.utils import getdate, add_days, add_months, nowdate
from frappe.utils.password import update_password
random.seed(2026)
leaf = lambda dt: frappe.db.get_value(dt, {"is_group": 0}, "name")
CO = [
  dict(name="Distribuidora Andina Demo S.A. (Sintética)", abbr="DAD", country="Panama", cur="USD", lang="es",
       user="es.demo@kodeerp.test", first="Demo", last="Español (Sintético)", pwenv="ES_PW", pl_s="Venta USD (Sintético)", pl_b="Compra USD (Sintético)",
       custs=["Supermercados La Estrella (Demo)", "Ferretería El Sol (Demo)", "Farmacia Central (Demo)", "Café Montaña Azul (Demo)", "Hotel Pacífico (Demo)", "Colegio San Martín (Demo)"],
       sups=["Importadora del Istmo (Demo)", "Textiles Andinos (Demo)", "Agroindustrias del Valle (Demo)"],
       items=[("ES-CAF-01", "Café molido 500 g (sintético)", 4.2, 7.5), ("ES-ARR-01", "Arroz premium 5 kg (sintético)", 5.1, 8.9),
              ("ES-ACE-01", "Aceite de girasol 1 L (sintético)", 2.3, 3.9), ("ES-AZU-01", "Azúcar refinada 2 kg (sintético)", 1.8, 3.2),
              ("ES-DET-01", "Detergente líquido 3 L (sintético)", 6.4, 10.5), ("ES-AGU-01", "Agua mineral 24 u (sintético)", 5.5, 9.0)]),
  dict(name="شركة الواحة للتجارة - تجريبية (Demo)", abbr="WTD", country="Saudi Arabia", cur="SAR", lang="ar",
       user="ar.demo@kodeerp.test", first="مستخدم", last="تجريبي (Demo)", pwenv="AR_PW", pl_s="بيع ريال (تجريبي)", pl_b="شراء ريال (تجريبي)",
       custs=["أسواق النخيل (تجريبي)", "مؤسسة الرياض للمقاولات (تجريبي)", "صيدلية الشفاء (تجريبي)", "مطاعم البحر الأحمر (تجريبي)", "مدارس المستقبل (تجريبي)"],
       sups=["مصنع الخليج للتغليف (تجريبي)", "شركة الأمل للإلكترونيات (تجريبي)", "مزارع القصيم (تجريبي)"],
       items=[("AR-TMR-01", "تمر سكري 1 كجم (تجريبي)", 18, 32), ("AR-QHW-01", "قهوة عربية 250 جم (تجريبي)", 22, 39),
              ("AR-ARZ-01", "أرز بسمتي 5 كجم (تجريبي)", 28, 45), ("AR-ZYT-01", "زيت زيتون 1 لتر (تجريبي)", 24, 41),
              ("AR-MIA-01", "مياه معدنية 12 عبوة (تجريبي)", 9, 16), ("AR-HLB-01", "حليب طويل الأجل 1 لتر (تجريبي)", 4, 7.5)]),
]
ROLES = ["Accounts User", "Sales User", "Purchase User", "Stock User"]
out = {}
for c in CO:
    if not frappe.db.exists("Company", c["name"]):
        frappe.get_doc({"doctype": "Company", "company_name": c["name"], "abbr": c["abbr"], "default_currency": c["cur"],
                        "country": c["country"], "chart_of_accounts": "Standard", "create_chart_of_accounts_based_on": "Standard Template"}).insert(ignore_permissions=True)
        frappe.db.commit()
    frappe.db.set_value("Currency", c["cur"], "enabled", 1)
    for pl, sell in ((c["pl_s"], 1), (c["pl_b"], 0)):
        if not frappe.db.exists("Price List", pl):
            frappe.get_doc({"doctype": "Price List", "price_list_name": pl, "currency": c["cur"], "selling": sell, "buying": 1 - sell, "enabled": 1}).insert(ignore_permissions=True)
    for n in c["custs"]:
        if not frappe.db.exists("Customer", n):
            frappe.get_doc({"doctype": "Customer", "customer_name": n, "customer_type": "Company", "customer_group": leaf("Customer Group"),
                            "territory": leaf("Territory"), "default_currency": c["cur"], "default_price_list": c["pl_s"], "language": c["lang"]}).insert(ignore_permissions=True)
    for n in c["sups"]:
        if not frappe.db.exists("Supplier", n):
            frappe.get_doc({"doctype": "Supplier", "supplier_name": n, "supplier_group": leaf("Supplier Group"), "default_currency": c["cur"],
                            "default_price_list": c["pl_b"]}).insert(ignore_permissions=True)
    for code, nm, cost, rate in c["items"]:
        if not frappe.db.exists("Item", code):
            frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": nm, "item_group": leaf("Item Group"), "stock_uom": "Nos",
                            "is_stock_item": 1, "valuation_rate": cost}).insert(ignore_permissions=True)
    # user
    if not frappe.db.exists("User", c["user"]):
        frappe.get_doc({"doctype": "User", "email": c["user"], "first_name": c["first"], "last_name": c["last"], "send_welcome_email": 0,
                        "user_type": "System User", "language": c["lang"]}).insert(ignore_permissions=True)
    u = frappe.get_doc("User", c["user"]); u.language = c["lang"]; u.enabled = 1
    u.roles = [r for r in u.roles if r.role in ROLES]
    for r in ROLES:
        if r not in [x.role for x in u.roles]: u.append("roles", {"role": r})
    u.save(ignore_permissions=True); update_password(c["user"], os.environ[c["pwenv"]])
    if not frappe.db.exists("User Permission", {"user": c["user"], "allow": "Company", "for_value": c["name"]}):
        frappe.get_doc({"doctype": "User Permission", "user": c["user"], "allow": "Company", "for_value": c["name"], "is_default": 1, "apply_to_all_doctypes": 1}).insert(ignore_permissions=True)
    frappe.db.commit()
    # transactions (Jul–Oct 2026, FY 2026-2027), skip if already seeded
    if frappe.db.count("Sales Invoice", {"company": c["name"]}):
        out[c["abbr"]] = "already seeded"; continue
    WH = f"Stores - {c['abbr']}"; ok = {"SE": 0, "PI": 0, "SI": 0, "PE": 0}; errs = []
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    def pay(dt, name, d):
        pe = get_payment_entry(dt, name); pe.posting_date = str(d); pe.reference_no = "SYN-" + name; pe.reference_date = str(d)
        pe.insert(ignore_permissions=True); pe.submit(); ok["PE"] += 1
    today = getdate(nowdate()); m = getdate("2026-07-01"); ev = []
    while m <= today:
        ev += [(m, "SE"), (add_days(m, 4), "PI")] + [(add_days(m, random.randint(2, 27)), "SI") for _ in range(7)]
        m = add_months(m, 1)
    ev = sorted([e for e in ev if getdate(e[0]) <= today], key=lambda e: (getdate(e[0]), e[1] != "SE"))
    for d, k in ev:
        d = str(d)
        try:
            if k == "SE":
                se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": c["name"], "posting_date": d, "set_posting_time": 1,
                    "items": [{"item_code": code, "qty": random.randint(40, 90), "t_warehouse": WH, "basic_rate": cost} for code, nm, cost, rate in c["items"]]})
                se.insert(ignore_permissions=True); se.submit()
            elif k == "PI":
                pi = frappe.get_doc({"doctype": "Purchase Invoice", "company": c["name"], "supplier": random.choice(c["sups"]), "posting_date": d, "set_posting_time": 1,
                    "bill_date": d, "due_date": add_days(d, 30), "currency": c["cur"], "buying_price_list": c["pl_b"], "update_stock": 1, "set_warehouse": WH,
                    "items": [{"item_code": code, "qty": random.randint(10, 30), "rate": cost, "warehouse": WH} for code, nm, cost, rate in random.sample(c["items"], 3)]})
                pi.insert(ignore_permissions=True); pi.submit()
                if getdate(add_days(d, 10)) <= today: pay("Purchase Invoice", pi.name, add_days(d, 10))
            else:
                si = frappe.get_doc({"doctype": "Sales Invoice", "company": c["name"], "customer": random.choice(c["custs"]), "posting_date": d, "set_posting_time": 1,
                    "due_date": add_days(d, 30), "currency": c["cur"], "selling_price_list": c["pl_s"], "update_stock": 1, "set_warehouse": WH,
                    "items": [{"item_code": code, "qty": random.randint(3, 20), "rate": rate, "warehouse": WH} for code, nm, cost, rate in random.sample(c["items"], random.randint(1, 4))]})
                si.insert(ignore_permissions=True); si.submit()
                if random.random() < 0.6 and getdate(add_days(d, 12)) <= today: pay("Sales Invoice", si.name, add_days(d, 12))
            ok[k] += 1; frappe.db.commit()
        except Exception as e:
            frappe.db.rollback(); errs.append(f"{k} {d}: {str(e)[:200]}")
    out[c["abbr"]] = {"created": ok, "errors": errs[:5], "n_err": len(errs)}
# keep the English demo user on its own company too
if not frappe.db.exists("User Permission", {"user": "demo@kodeerp.test", "allow": "Company"}):
    frappe.get_doc({"doctype": "User Permission", "user": "demo@kodeerp.test", "allow": "Company", "for_value": "Kodenova Demo Trading (Synthetic)", "is_default": 1, "apply_to_all_doctypes": 1}).insert(ignore_permissions=True)
for l in ("es", "ar"): frappe.db.set_value("Language", l, "enabled", 1)
frappe.db.commit()
print(out)
