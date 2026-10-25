# Apply "accounting only" navigation on fnb.localhost. Run with:
#   sudo docker exec -u frappe kodeerp-frappe-1 /workspace/development/run_site_script.sh fnb.localhost /workspace/development/fnb_accounting_only_apply.py
# Settings only (DB records on fnb): Module Profile + user assignment, site-layer Custom Sidebar for
# "Kodenova Theme" and "Accounts", one card in the fnb copy of Custom HTML Block "KodeERP Quick Actions",
# and Translation rows for the new card text. Pre-state is saved for undo.
import frappe, json, os
assert frappe.local.site == "fnb.localhost", "fnb only"
from frappe.desk.doctype.custom_sidebar.custom_sidebar import get_site_sidebar_layer, save_site_sidebar
from frappe.utils.modules import get_blockable_module_names
STATE = "/workspace/development/fnb_accounting_only_prestate.json"
PROFILE = "KodeERP Accounting Only (F&B)"
KEEP = {"Accounts", "Kodenova Theme"}
USERS = [u for u in frappe.get_all("User", filters={"user_type": "System User", "enabled": 1, "name": ["not in", ["Administrator"]]}, pluck="name")
         if "System Manager" not in frappe.get_roles(u)]
pre = json.load(open(STATE)) if os.path.exists(STATE) else {}
if not pre:
    pre["users"] = {u: {"module_profile": frappe.db.get_value("User", u, "module_profile"),
                        "block_modules": [d.module for d in frappe.get_doc("User", u).block_modules]} for u in USERS}
    pre["custom_sidebars"] = frappe.get_all("Custom Sidebar", filters={"user": ["in", ["", None]]}, pluck="name")
    pre["quick_actions_html"] = frappe.db.get_value("Custom HTML Block", "KodeERP Quick Actions", "html")
    json.dump(pre, open(STATE, "w"), ensure_ascii=False, indent=1)

# 1. Module Profile
blocked = [m for m in get_blockable_module_names() if m not in KEEP]
mp = frappe.get_doc("Module Profile", PROFILE) if frappe.db.exists("Module Profile", PROFILE) else frappe.new_doc("Module Profile")
mp.module_profile_name = PROFILE
mp.set("block_modules", [{"module": m} for m in blocked])
mp.save(ignore_permissions=True)
for u in USERS:
    d = frappe.get_doc("User", u); d.module_profile = PROFILE; d.save(ignore_permissions=True)
print("profile blocks", len(blocked), "modules; users:", USERS)

# 2. Site sidebar: KodeERP (Kodenova Theme)
def link(label, lt, to, icon): return {"type": "Link", "label": label, "link_type": lt, "link_to": to, "icon": icon, "child": 1, "added": 1}
base = {r["key"]: r for r in get_site_sidebar_layer("Kodenova Theme")}
order = []
for r in get_site_sidebar_layer("Kodenova Theme"):
    if r.get("added"): continue
    r = dict(r); r["hidden"] = 1 if r.get("link_to") in ("Quotation", "Selling", "Buying", "Stock") else 0
    order.append(r)
    if r.get("link_to") == "Sales Invoice":
        order += [link("Purchase Invoice", "DocType", "Purchase Invoice", "receipt"), link("POS Invoice", "DocType", "POS Invoice", "monitor")]
    if r.get("link_to") == "Payment Entry":
        order += [link("Journal Entry", "DocType", "Journal Entry", "book-open")]
    if r.get("link_to") == "Customer":
        order += [link("Supplier", "DocType", "Supplier", "truck")]
    if r.get("link_to") == "Accounting":
        order += [link("Financial Reports", "Workspace", "Financial Reports", "chart-column")]
save_site_sidebar("Kodenova Theme", json.dumps(order))

# 3. Site sidebar: Accounts — add masters, branch, POS and VAT return
acc = [dict(r) for r in get_site_sidebar_layer("Accounts") if not r.get("added")]
extra = [{"type": "Section Break", "label": "Masters & POS", "collapsible": 1, "added": 1, "child": 0},
         link("Customer", "DocType", "Customer", "user-round"), link("Supplier", "DocType", "Supplier", "truck"),
         link("Item", "DocType", "Item", "package"), link("Branch", "DocType", "Branch", "git-branch"),
         link("POS Invoice", "DocType", "POS Invoice", "monitor"),
         link("KSA VAT Return (Demo) | إقرار ضريبة القيمة المضافة", "Report", "KSA VAT Return (Demo) | إقرار ضريبة القيمة المضافة", "percent")]
# insert after the Reports section's last item (before "Banking")
i = next((n for n, r in enumerate(acc) if r.get("type") == "Section Break" and r.get("label") == "Banking"), len(acc))
save_site_sidebar("Accounts", json.dumps(acc[:i] + extra + acc[i:]))

# 4. Quick actions: replace the Quotation card with Purchase Invoice (fnb copy only)
import re
h = pre["quick_actions_html"]
m = re.search(r'<article class="kd-plan" data-doctype="Quotation".*?</article>', h, re.S)
if m:
    card = m.group(0)
    card = card.replace('data-doctype="Quotation"', 'data-doctype="Purchase Invoice"')
    card = re.sub(r'<span class="kd-tag" data-i18n>[^<]*</span>', '<span class="kd-tag" data-i18n>Purchases</span>', card)
    card = re.sub(r'<h3 data-i18n>[^<]*</h3>', '<h3 data-i18n>New purchase invoice</h3>', card)
    card = re.sub(r'<p data-i18n>[^<]*</p>', '<p data-i18n>Record a supplier bill with VAT.</p>', card)
    spans = iter(["Input VAT tracked", "Branch cost centre"])
    card = re.sub(r'(<li>.*?<span data-i18n>)[^<]*(</span></li>)', lambda mm: mm.group(1) + next(spans, "") + mm.group(2), card, flags=re.S)
    card = re.sub(r'(<button[^>]*><span data-i18n>)[^<]*(</span>)', r'\1New purchase invoice\2', card)
    frappe.db.set_value("Custom HTML Block", "KodeERP Quick Actions", "html", h.replace(m.group(0), card))
tr = {"Purchases": ("المشتريات", "Compras"), "New purchase invoice": ("فاتورة شراء جديدة", "Nueva factura de compra"),
      "Record a supplier bill with VAT.": ("سجّل فاتورة المورد مع ضريبة القيمة المضافة.", "Registra una factura de proveedor con IVA."),
      "Input VAT tracked": ("تتبع ضريبة المدخلات", "IVA soportado registrado"), "Branch cost centre": ("مركز تكلفة الفرع", "Centro de costo de sucursal"),
      "Masters & POS": ("البيانات الأساسية ونقاط البيع", "Maestros y POS")}
for src, (ar, es) in tr.items():
    for lang, txt in (("ar", ar), ("es", es)):
        if not frappe.db.exists("Translation", {"language": lang, "source_text": src}):
            frappe.get_doc({"doctype": "Translation", "language": lang, "source_text": src, "translated_text": txt}).insert(ignore_permissions=True)
frappe.clear_cache()
print("applied")
