#!/usr/bin/env python3
"""API test for the Foodics-aligned fnb setup, as each demo user, on 127.0.0.1:8093. Passwords read from .secrets, never printed.
Creates QA TEST docs and cancels them at the end. Usage: python3 verify/fnb_foodics_aligned_test.py [--admin-cleanup-file]"""
import json, os, re, sys, urllib.request, urllib.parse, datetime, calendar
BASE = "http://127.0.0.1:8093"; S = "/workspace/kodeerp/.secrets/"; CO = "Najd Bites Food Co."
USERS = [("najd.accounts.en@kodeerp.test", "fnb_en_password", "Malqa, Riyadh | الملقا - الرياض", "Malqa Kitchen | مطبخ الملقا - NJB"),
         ("najd.accounts.ar@kodeerp.test", "fnb_ar_password", "Tahlia, Jeddah | التحلية - جدة", "Tahlia Kitchen | مطبخ التحلية - NJB"),
         ("najd.olaya.manager@kodeerp.test", "fnb_branch_password", "Olaya, Riyadh | العليا - الرياض", "Olaya Kitchen | مطبخ العليا - NJB")]
if len(sys.argv) > 1 and sys.argv[1] != "all": USERS = [u for u in USERS if u[0].startswith(sys.argv[1])]
T = datetime.date.today(); TODAY = T.isoformat(); MSTART = T.replace(day=1).isoformat()
MEND = T.replace(day=calendar.monthrange(T.year, T.month)[1]).isoformat()
TAX = "KSA VAT 15% | ضريبة القيمة المضافة 15% - NJB"; CFS = "Central Food Store | مخزن الأغذية المركزي - NJB"
results = {}; created = []
class C:
    def __init__(s): s.op = urllib.request.build_opener(); s.ck = {}; s.csrf = ""
    def r(s, m, p, data=None, raw=False):
        body = json.dumps(data).encode() if data is not None else None
        rq = urllib.request.Request(BASE + urllib.parse.quote(p, safe="/?=&%:"), data=body, method=m, headers={"Content-Type": "application/json", "Accept": "application/json", "X-Frappe-CSRF-Token": s.csrf, "Cookie": "; ".join(f"{k}={v}" for k, v in s.ck.items())})
        try:
            with s.op.open(rq, timeout=180) as x: t = x.read().decode(); code = x.status; hd = x.headers
        except urllib.error.HTTPError as e: t = e.read().decode(); code = e.code; hd = e.headers
        for sc in hd.get_all("Set-Cookie") or []:
            k, _, v = sc.split(";")[0].partition("="); s.ck[k.strip()] = v
        if raw: return code, t
        try: return code, json.loads(t)
        except Exception: return code, t[:300]
    def call(s, method, **kw): return s.r("POST", "/api/method/" + method, kw)
    def get(s, method, **kw): return s.r("GET", "/api/method/" + method + "?" + urllib.parse.urlencode(kw, quote_via=urllib.parse.quote))
def err(d):
    if isinstance(d, dict):
        m = d.get("_server_messages") or d.get("exception") or d.get("exc_type") or ""
        try: m = " ".join(json.loads(x).get("message", "") for x in json.loads(m)) if str(m).startswith("[") else m
        except Exception: pass
        return re.sub(r"<[^>]+>", "", str(m))[:300]
    return str(d)[:300]
def check(u, name, ok, info=""):
    results.setdefault(u, []).append((name, "PASS" if ok else "FAIL", info)); print(f"  [{'PASS' if ok else 'FAIL'}] {name} {info}", flush=True); return ok
def mk(c, u, label, doc, submit=True):
    code, d = c.r("POST", "/api/resource/" + doc["doctype"], doc)
    if code != 200: check(u, label + " insert", False, f"HTTP {code} " + err(d)); return None
    doc = d["data"]
    if submit:
        code, d2 = c.call("frappe.client.submit", doc=doc)
        if code != 200: check(u, label + " submit", False, doc["name"] + " " + err(d2)); created.append((c, u, doc["doctype"], doc["name"], 0)); return None
        doc = d2["message"]
    check(u, label + (" insert+submit" if submit else " insert"), True, doc["name"]); created.append((c, u, doc["doctype"], doc["name"], int(submit))); return doc
EXPECT = ["Quotation", "Purchase Order", "Stock Entry", "Stock Reconciliation", "Asset", "Employee", "Salary Slip", "Payroll Entry", "Bank Reconciliation Tool", "Employee Advance", "Additional Salary", "Landed Cost Voucher", "Opening Invoice Creation Tool"]
for u, pwf, branch, wh in USERS:
    tag = u.split("@")[0].split(".")[-1]
    print("==", u, flush=True); c = C()
    code, d = c.call("login", usr=u, pwd=open(S + pwf).read().strip()); check(u, "login", code == 200)
    code, html = c.r("GET", "/app", raw=True)
    cm = re.search(r'csrf_token\s*[=:]\s*"([^"]+)"', html); c.csrf = cm.group(1) if cm else ""
    bm = re.search(r'frappe\.boot\s*=\s*\{', html); boot = {}
    if bm: boot = json.JSONDecoder().raw_decode(html[bm.end()-1:])[0]
    keys = sorted(boot.get("module_sidebars", {}).keys())
    check(u, "desk boot: only Accounts + KodeERP sidebars", set(keys) <= {"Accounts", "KodeERP"} and keys, f"sidebars={keys} lang={boot.get('lang')}")
    items = boot.get("module_sidebars", {}).get("KodeERP", {}).get("items", [])
    secs = [i["label"] for i in items if i.get("type") == "Section Break"]; links = {i.get("link_to") for i in items}
    check(u, "KodeERP sidebar sections", True, " / ".join(secs))
    miss = [e for e in EXPECT if e not in links]; check(u, "sidebar has the new doctypes", not miss, "missing=" + str(miss) if miss else f"{len(items)} items")
    bad = [i["label"] for i in items if re.search(r"erpnext|frappe", (i.get("label") or ""), re.I)]; check(u, "no ERPNext/Frappe label in sidebar", not bad, str(bad))
    blocked = [x for x in ("CRM", "Lead", "Opportunity", "BOM", "Work Order", "Project", "Issue", "Quality Inspection", "Web Page", "Sales Order", "Delivery Note") if x in links]
    check(u, "CRM/Manufacturing/Projects/Support/Website not in sidebar", not blocked, str(blocked))
    # Quotation
    mk(c, u, "Quotation", {"doctype": "Quotation", "company": CO, "quotation_to": "Customer", "party_name": "Al-Faisal Medical Clinic (Demo) | عيادة الفيصل الطبية",
       "transaction_date": TODAY, "valid_till": MEND, "branch": branch, "taxes_and_charges": TAX, "items": [{"item_code": "MN-001", "qty": 1, "rate": 10}],
       "terms": "QA TEST Foodics-aligned check (will be cancelled)"})
    # Purchase Order
    mk(c, u, "Purchase Order", {"doctype": "Purchase Order", "company": CO, "supplier": "Golden Bakery (Demo) | المخبز الذهبي", "transaction_date": TODAY, "schedule_date": TODAY,
       "branch": branch, "set_warehouse": wh, "taxes_and_charges": TAX, "items": [{"item_code": "RM-006", "qty": 1, "rate": 0.5, "schedule_date": TODAY, "warehouse": wh}],
       "terms": "QA TEST Foodics-aligned check (will be cancelled)"})
    # Stock Entry: material transfer central store -> branch kitchen
    mk(c, u, "Stock Entry (Material Transfer)", {"doctype": "Stock Entry", "company": CO, "stock_entry_type": "Material Transfer", "posting_date": TODAY, "set_posting_time": 1,
       "remarks": "QA TEST Foodics-aligned check (will be cancelled)", "items": [{"item_code": "RM-006", "qty": 1, "s_warehouse": CFS, "t_warehouse": wh}]})
    # Stock Reconciliation (count): current qty + 1
    code, d = c.get("frappe.client.get_value", doctype="Bin", filters=json.dumps({"item_code": "RM-006", "warehouse": wh}), fieldname="actual_qty")
    q = (d.get("message") or {}).get("actual_qty") if code == 200 else None
    if check(u, "read stock qty (Bin)", q is not None, f"qty={q}" if q is not None else err(d)):
        mk(c, u, "Stock Reconciliation", {"doctype": "Stock Reconciliation", "company": CO, "purpose": "Stock Reconciliation", "posting_date": TODAY, "set_posting_time": 1,
           "expense_account": "Stock Adjustment | تسوية المخزون - NJB", "items": [{"item_code": "RM-006", "warehouse": wh, "qty": q + 1, "valuation_rate": 0.5}]})
    # Asset (existing asset, available today -> no GL until first depreciation date)
    mk(c, u, "Asset", {"doctype": "Asset", "company": CO, "item_code": "FA-001", "asset_name": f"QA TEST Oven {tag}", "asset_category": "Kitchen Equipment | معدات المطبخ",
       "location": "Najd Bites HQ | المقر الرئيسي", "branch": branch, "is_existing_asset": 1, "gross_purchase_amount": 6000, "net_purchase_amount": 6000, "purchase_amount": 6000, "purchase_date": TODAY,
       "available_for_use_date": TODAY, "calculate_depreciation": 1,
       "finance_books": [{"depreciation_method": "Straight Line", "total_number_of_depreciations": 60, "frequency_of_depreciation": 1, "depreciation_start_date": MEND}]})
    # HR: Employee -> Salary Structure Assignment -> Salary Slip
    emp = mk(c, u, "Employee", {"doctype": "Employee", "first_name": "QA TEST", "last_name": tag, "gender": "Male", "date_of_birth": "1990-01-01", "date_of_joining": "2026-01-01",
             "company": CO, "branch": branch, "holiday_list": "KSA Weekends 2026 | عطلات نهاية الأسبوع 2026", "status": "Active"}, submit=False)
    if emp:
        ssa = mk(c, u, "Salary Structure Assignment", {"doctype": "Salary Structure Assignment", "employee": emp["name"], "salary_structure": "Najd Standard Monthly | الهيكل الشهري القياسي",
                 "company": CO, "currency": "SAR", "from_date": "2026-01-01", "base": 6000})
        if ssa:
            ss = mk(c, u, "Salary Slip", {"doctype": "Salary Slip", "employee": emp["name"], "company": CO, "start_date": MSTART, "end_date": MEND, "posting_date": TODAY, "payroll_frequency": "Monthly"})
            if ss: check(u, "Salary Slip amounts", ss.get("gross_pay") == 6000, f"gross={ss.get('gross_pay')} net={ss.get('net_pay')} working_days={ss.get('total_working_days')}")
    # Bank Reconciliation Tool opens + balance call
    code, d = c.get("frappe.desk.form.load.getdoc", doctype="Bank Reconciliation Tool", name="Bank Reconciliation Tool")
    check(u, "Bank Reconciliation Tool opens", code == 200, "" if code == 200 else f"HTTP {code} " + err(d))
    code, d = c.get("erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.get_account_balance",
                    bank_account="Najd Bites Current - Demo Bank | البنك التجريبي", till_date=TODAY, company=CO)
    check(u, "Bank Reconciliation balance call", code == 200, f"balance={d.get('message')}" if code == 200 else f"HTTP {code} " + err(d))
    # Other forms open (read)
    for dt in ("Opening Invoice Creation Tool",):
        code, d = c.get("frappe.desk.form.load.getdoc", doctype=dt, name=dt); check(u, dt + " opens", code == 200, "" if code == 200 else f"HTTP {code} " + err(d))
    for dt in ("Landed Cost Voucher", "Payroll Entry", "Additional Salary", "Employee Advance", "Leave Application", "Asset Movement", "Auto Repeat", "Journal Entry Template", "Repost Item Valuation", "Bank Transaction"):
        code, d = c.get("frappe.desk.reportview.get_count", doctype=dt); check(u, "list " + dt, code == 200, "" if code == 200 else f"HTTP {code} " + err(d))
    # Reports
    FY = {"company": CO, "filter_based_on": "Fiscal Year", "from_fiscal_year": "2026", "to_fiscal_year": "2026", "periodicity": "Yearly", "period_start_date": "2026-01-01", "period_end_date": "2026-12-31"}
    for rep, flt in [("Trial Balance", {"company": CO, "fiscal_year": "2026", "from_date": "2026-01-01", "to_date": "2026-12-31"}), ("Cash Flow", FY), ("Profitability Analysis", {"company": CO, "based_on": "Cost Center", "fiscal_year": "2026", "from_date": "2026-01-01", "to_date": "2026-12-31"}),
                     ("Gross Profit", {"company": CO, "from_date": "2026-01-01", "to_date": TODAY, "group_by": "Invoice"}),
                     ("Customer Ledger Summary", {"company": CO, "from_date": "2026-01-01", "to_date": TODAY}), ("Supplier Ledger Summary", {"company": CO, "from_date": "2026-01-01", "to_date": TODAY}),
                     ("Bank Reconciliation Statement", {"company": CO, "account": "Bank - Demo Current Account | الحساب الجاري البنكي (تجريبي) - NJB", "report_date": TODAY}),
                     ("Stock Balance", {"company": CO, "from_date": MSTART, "to_date": TODAY}), ("Fixed Asset Register", {"company": CO, "status": "In Location", "filter_based_on": "Fiscal Year", "from_fiscal_year": "2026", "to_fiscal_year": "2026", "date_based_on": "Purchase Date", "group_by": "--Select a group--"}),
                     ("Salary Register", {"company": CO, "from_date": MSTART, "to_date": MEND, "docstatus": "Submitted", "currency": "SAR"}),
                     ("KSA VAT Return (Demo) | إقرار ضريبة القيمة المضافة", {"company": CO, "from_date": "2026-01-01", "to_date": TODAY})]:
        code, d = c.call("frappe.desk.query_report.run", report_name=rep, filters=json.dumps(flt), ignore_prepared_report=1)
        ok = code == 200 and isinstance(d, dict) and "message" in d
        check(u, "report " + rep.split(" |")[0], ok, (f"rows={len(d['message'].get('result') or [])}" if ok else f"HTTP {code} " + err(d)))
    c.user = u
json.dump({"created": [(u, dt, n, s) for _, u, dt, n, s in created], "results": results}, open("/workspace/kodeerp/verify/fnb_foodics_aligned_result.json", "w"), ensure_ascii=False, indent=1)
# cleanup: cancel submitted docs as the creating user, newest first
print("== cleanup (cancel as user)")
for c, u, dt, n, sub in reversed(created):
    if not sub: continue
    code, d = c.call("frappe.client.cancel", doctype=dt, name=n)
    print(f"  cancel {dt} {n} as {u.split('@')[0]}: {'OK' if code == 200 else 'NEEDS ADMIN - ' + err(d)}", flush=True)
