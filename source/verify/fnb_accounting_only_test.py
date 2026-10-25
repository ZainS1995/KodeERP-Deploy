#!/usr/bin/env python3
"""API test for the fnb accounting-only setup, as each demo user, on 127.0.0.1:8093. Passwords read from .secrets, never printed."""
import json, os, re, sys, urllib.request, urllib.parse, http.cookiejar, datetime
BASE = "http://127.0.0.1:8093"; S = "/workspace/kodeerp/.secrets/"
USERS = [("najd.accounts.en@kodeerp.test", "fnb_en_password", "Malqa, Riyadh | الملقا - الرياض"),
         ("najd.accounts.ar@kodeerp.test", "fnb_ar_password", "Tahlia, Jeddah | التحلية - جدة"),
         ("najd.olaya.manager@kodeerp.test", "fnb_branch_password", "Olaya, Riyadh | العليا - الرياض")]
TODAY = datetime.date.today().isoformat()
TAX = "KSA VAT 15% | ضريبة القيمة المضافة 15% - NJB"
results = {}; created = []
class C:
    def __init__(s): s.op = urllib.request.build_opener(); s.ck = {}
    def r(s, m, p, data=None, raw=False):
        body = json.dumps(data).encode() if data is not None else None
        rq = urllib.request.Request(BASE + urllib.parse.quote(p, safe="/?=&%:"), data=body, method=m, headers={"Content-Type": "application/json", "Accept": "application/json", "X-Frappe-CSRF-Token": getattr(s, "csrf", ""), "Cookie": "; ".join(f"{k}={v}" for k, v in s.ck.items())})
        try:
            with s.op.open(rq, timeout=120) as x: t = x.read().decode(); code = x.status; hd = x.headers
        except urllib.error.HTTPError as e: t = e.read().decode(); code = e.code; hd = e.headers
        for sc in hd.get_all("Set-Cookie") or []:
            k, _, v = sc.split(";")[0].partition("="); s.ck[k.strip()] = v
        if raw: return code, t
        try: return code, json.loads(t)
        except Exception: return code, t[:300]
    def call(s, method, **kw): return s.r("POST", "/api/method/" + method, kw)
def err(d):
    if isinstance(d, dict):
        m = d.get("_server_messages") or d.get("exception") or d.get("exc_type") or ""
        return str(m)[:300]
    return str(d)[:300]
def check(u, name, ok, info=""):
    results.setdefault(u, []).append((name, "PASS" if ok else "FAIL", info)); print(f"  [{'PASS' if ok else 'FAIL'}] {name} {info}")
for u, pwf, branch in USERS:
    print("==", u); c = C()
    code, d = c.call("login", usr=u, pwd=open(S + pwf).read().strip()); check(u, "login", code == 200)
    code, html = c.r("GET", "/app", raw=True)
    cm = re.search(r'csrf_token\s*[=:]\s*"([^"]+)"', html); c.csrf = cm.group(1) if cm else ""
    m = re.search(r'"module_sidebars":\s*\{', html)
    mods = sorted(set(re.findall(r'"module":\s*"([^"]+)"', html[m.start(): m.start() + 400000]))) if m else []
    # top-level module_sidebars keys: parse boot JSON
    bm = re.search(r'frappe\.boot\s*=\s*\{', html)
    keys = []; lang = "?"
    if bm:
        try: boot = json.JSONDecoder().raw_decode(html[bm.end()-1:])[0]; keys = sorted(boot.get("module_sidebars", {}).keys()); lang = boot.get("lang")
        except Exception as e: keys = ["parse-error " + str(e)[:80]]; lang = "?"
    check(u, "desk boot: only accounting sidebars", keys and set(keys) <= {"Accounts", "KodeERP"}, f"sidebars={keys} lang={lang}")
    # Sales Invoice
    si = {"doctype": "Sales Invoice", "company": "Najd Bites Food Co.", "customer": "Al-Faisal Medical Clinic (Demo) | عيادة الفيصل الطبية",
          "branch": branch, "posting_date": TODAY, "set_posting_time": 1, "due_date": TODAY, "taxes_and_charges": TAX, "remarks": "QA TEST accounting-only check (will be cancelled)",
          "items": [{"item_code": "MN-001", "qty": 1, "rate": 10}]}
    code, d = c.r("POST", "/api/resource/Sales Invoice", si)
    if code == 200:
        doc = d["data"]; check(u, "SI insert", True, f"{doc['name']} cc={doc.get('cost_center')} total={doc.get('grand_total')}")
        code, d = c.call("frappe.client.submit", doc=doc); ok = code == 200; check(u, "SI submit", ok, "" if ok else err(d))
        if ok: created.append((c, "Sales Invoice", doc["name"]))
        if ok:
            code, d = c.r("GET", "/api/method/erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry?" + urllib.parse.urlencode({"dt": "Sales Invoice", "dn": doc["name"]}, quote_via=urllib.parse.quote))
            if code == 200:
                pe = d["message"]; pe.update({"mode_of_payment": "Cash | نقدي" if False else pe.get("mode_of_payment"), "reference_no": "QA TEST", "reference_date": TODAY, "remarks": "QA TEST accounting-only check (will be cancelled)"})
                code, d = c.r("POST", "/api/resource/Payment Entry", pe)
                if code == 200:
                    code2, d2 = c.call("frappe.client.submit", doc=d["data"]); ok = code2 == 200
                    check(u, "Payment Entry insert+submit", ok, d["data"]["name"] + ("" if ok else " " + err(d2)))
                    if ok: created.append((c, "Payment Entry", d["data"]["name"]))
                else: check(u, "Payment Entry insert", False, err(d))
            else: check(u, "get_payment_entry", False, err(d))
    else: check(u, "SI insert", False, err(d))
    if os.environ.get("PE_ONLY"): continue
    # Purchase Invoice
    pi = {"doctype": "Purchase Invoice", "company": "Najd Bites Food Co.", "supplier": "Golden Bakery (Demo) | المخبز الذهبي", "branch": branch,
          "posting_date": TODAY, "set_posting_time": 1, "due_date": TODAY, "bill_no": "QA-TEST-" + u.split("@")[0], "bill_date": TODAY, "update_stock": 0, "taxes_and_charges": TAX,
          "remarks": "QA TEST accounting-only check (will be cancelled)", "items": [{"item_code": "RM-006", "qty": 1, "rate": 10}]}
    code, d = c.r("POST", "/api/resource/Purchase Invoice", pi)
    if code == 200:
        doc = d["data"]; code, d2 = c.call("frappe.client.submit", doc=doc); ok = code == 200
        check(u, "PI insert+submit", ok, f"{doc['name']} cc={doc.get('cost_center')}" + ("" if ok else " " + err(d2)))
        if ok: created.append((c, "Purchase Invoice", doc["name"]))
    else: check(u, "PI insert", False, f"HTTP {code} " + err(d))
    # Reports
    for rep, flt in [("General Ledger", {"company": "Najd Bites Food Co.", "from_date": "2026-01-01", "to_date": TODAY, "group_by": "Group by Voucher (Consolidated)"}),
                     ("Trial Balance", {"company": "Najd Bites Food Co.", "fiscal_year": "2026", "from_date": "2026-01-01", "to_date": "2026-12-31"}),
                     ("Profit and Loss Statement", {"company": "Najd Bites Food Co.", "filter_based_on": "Fiscal Year", "from_fiscal_year": "2026", "to_fiscal_year": "2026", "periodicity": "Yearly"}),
                     ("Balance Sheet", {"company": "Najd Bites Food Co.", "filter_based_on": "Fiscal Year", "from_fiscal_year": "2026", "to_fiscal_year": "2026", "periodicity": "Yearly"}),
                     ("Accounts Receivable", {"company": "Najd Bites Food Co.", "report_date": TODAY, "ageing_based_on": "Due Date", "range": "30, 60, 90, 120"}),
                     ("Accounts Payable", {"company": "Najd Bites Food Co.", "report_date": TODAY, "ageing_based_on": "Due Date", "range": "30, 60, 90, 120"}),
                     ("KSA VAT Return (Demo) | إقرار ضريبة القيمة المضافة", {"company": "Najd Bites Food Co.", "from_date": "2026-01-01", "to_date": TODAY})]:
        code, d = c.call("frappe.desk.query_report.run", report_name=rep, filters=json.dumps(flt), ignore_prepared_report=1)
        ok = code == 200 and isinstance(d, dict) and "message" in d
        check(u, "report " + rep.split(" |")[0], ok, (f"rows={len(d['message'].get('result') or [])}" if ok else f"HTTP {code} " + err(d)))
# cancel in reverse order (PE before SI)
print("== cleanup")
for c, dt, n in reversed(created):
    code, d = c.call("frappe.client.cancel", doctype=dt, name=n)
    print(f"  cancel {dt} {n}: {'OK' if code == 200 else 'FAIL ' + err(d)}")
    if code != 200: results.setdefault("cleanup", []).append((dt, n))
json.dump({"created": [(dt, n) for _, dt, n in created], "results": results}, open("/workspace/kodeerp/verify/fnb_accounting_only_result" + ("_pe" if os.environ.get("PE_ONLY") else "") + ".json", "w"), ensure_ascii=False, indent=1)
