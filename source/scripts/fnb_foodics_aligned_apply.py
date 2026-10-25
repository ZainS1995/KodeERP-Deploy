# Foodics-aligned navigation + roles on fnb.localhost (builds on fnb_accounting_only_apply.py). Run with:
#   cp scripts/fnb_foodics_aligned_apply.py development/ && sudo docker exec -u frappe kodeerp-frappe-1 \
#     /workspace/development/run_site_script.sh fnb.localhost /workspace/development/fnb_foodics_aligned_apply.py
# Site records only (no core/app code). Idempotent. Pre-state saved to fnb_foodics_prestate.json for undo.
import frappe, json, os
from frappe.utils import getdate
assert frappe.local.site == "fnb.localhost", "fnb only"
from frappe.desk.doctype.custom_sidebar.custom_sidebar import get_site_sidebar_layer, save_site_sidebar
from frappe.permissions import add_permission, update_permission_property
STATE = "/workspace/development/fnb_foodics_prestate.json"
CO = "Najd Bites Food Co."
EN, AR, MG = "najd.accounts.en@kodeerp.test", "najd.accounts.ar@kodeerp.test", "najd.olaya.manager@kodeerp.test"
ADD_ROLES = {EN: ["HR User", "HR Manager", "Expense Approver"], AR: ["HR User", "HR Manager", "Expense Approver"],
             MG: ["Purchase User", "Stock Manager", "HR User"]}
PERMS = {"Bank Reconciliation Tool": {"Accounts Manager": ("read", "write", "create"), "Accounts User": ("read", "write")},
         "Opening Invoice Creation Tool": {"Accounts Manager": ("read", "write", "create")}}
HL = "KSA Weekends 2026 | عطلات نهاية الأسبوع 2026"
SS = "Najd Standard Monthly | الهيكل الشهري القياسي"
AC = "Kitchen Equipment | معدات المطبخ"
IG = "Fixed Assets | الأصول الثابتة"
LOC = "Najd Bites HQ | المقر الرئيسي"
pre = json.load(open(STATE)) if os.path.exists(STATE) else {}
if not pre:
    pre = {"roles": {u: frappe.get_roles(u) for u in ADD_ROLES},
           "custom_docperm": {d: bool(frappe.db.exists("Custom DocPerm", {"parent": d})) for d in PERMS},
           "kodeerp_sidebar": get_site_sidebar_layer("Kodenova Theme"),
           "company_holiday_list": frappe.db.get_value("Company", CO, "default_holiday_list"),
           "basic_accounts": [a.as_dict() for a in frappe.get_doc("Salary Component", "Basic").accounts],
           "created": [], "translations_created": []}
    json.dump(pre, open(STATE, "w"), ensure_ascii=False, indent=1, default=str)
def created(dt, name):
    if [dt, name] not in pre["created"]: pre["created"].append([dt, name])

# 1. Roles (no CRM/Sales Manager/System Manager added)
for u, roles in ADD_ROLES.items():
    d = frappe.get_doc("User", u); have = {r.role for r in d.roles}
    for r in roles:
        if r not in have: d.append("roles", {"role": r})
    d.save(ignore_permissions=True)
    print("roles", u, sorted(frappe.get_roles(u)))

# 2. Custom DocPerms for two System-Manager-only tools (add_permission copies the standard rows first)
for dt, roles in PERMS.items():
    for role, ptypes in roles.items():
        add_permission(dt, role, 0)
        for p in ptypes: update_permission_property(dt, role, 0, p, 1)
frappe.clear_cache()

# 3. Demo masters (synthetic) so HR/payroll and assets can be used
if not frappe.db.exists("Holiday List", HL):
    hl = frappe.get_doc({"doctype": "Holiday List", "holiday_list_name": HL, "from_date": "2026-01-01", "to_date": "2026-12-31",
                         "holidays": [{"holiday_date": "2026-02-22", "description": "Founding Day | يوم التأسيس"},
                                      {"holiday_date": "2026-09-23", "description": "National Day | اليوم الوطني"}]})
    for wd in ("Friday", "Saturday"):
        hl.weekly_off = wd; hl.get_weekly_off_dates()
    hl.insert(ignore_permissions=True); created("Holiday List", HL)
frappe.db.set_value("Company", CO, "default_holiday_list", HL)
if not frappe.db.exists("Holiday List Assignment", {"assigned_to": CO, "holiday_list": HL, "docstatus": 1}):
    hla = frappe.get_doc({"doctype": "Holiday List Assignment", "applicable_for": "Company", "assigned_to": CO, "holiday_list": HL, "from_date": "2026-01-01"})
    hla.insert(ignore_permissions=True); hla.submit(); created("Holiday List Assignment", hla.name)
SP = "Salaries Payable | الرواتب المستحقة - NJB"  # HRMS requires account_type Payable on the payroll payable account
pre.setdefault("salaries_payable_type", frappe.db.get_value("Account", SP, "account_type"))
frappe.db.set_value("Account", SP, "account_type", "Payable")
b = frappe.get_doc("Salary Component", "Basic")
if not any(a.company == CO for a in b.accounts):
    b.append("accounts", {"company": CO, "account": "Basic Salaries | الرواتب الأساسية - NJB"}); b.save(ignore_permissions=True)
for name, abbr, acct in (("Housing Allowance | بدل السكن", "HA", "Housing Allowance | بدل السكن - NJB"),
                         ("Overtime | العمل الإضافي", "OT", "Basic Salaries | الرواتب الأساسية - NJB")):
    if not frappe.db.exists("Salary Component", name):
        frappe.get_doc({"doctype": "Salary Component", "salary_component": name, "salary_component_abbr": abbr, "type": "Earning",
                        "accounts": [{"company": CO, "account": acct}]}).insert(ignore_permissions=True); created("Salary Component", name)
if not frappe.db.exists("Salary Structure", SS):
    s = frappe.get_doc({"doctype": "Salary Structure", "name": SS, "__newname": SS, "company": CO, "currency": "SAR", "payroll_frequency": "Monthly", "is_active": "Yes",
                        "earnings": [{"salary_component": "Basic", "abbr": "B", "amount_based_on_formula": 1, "formula": "base * 0.75"},
                                     {"salary_component": "Housing Allowance | بدل السكن", "abbr": "HA", "amount_based_on_formula": 1, "formula": "base * 0.25"}]})
    s.insert(ignore_permissions=True); s.submit(); created("Salary Structure", s.name)
if not frappe.db.exists("Item Group", IG):
    frappe.get_doc({"doctype": "Item Group", "item_group_name": IG, "parent_item_group": "All Item Groups"}).insert(ignore_permissions=True); created("Item Group", IG)
if not frappe.db.exists("Asset Category", AC):
    frappe.get_doc({"doctype": "Asset Category", "asset_category_name": AC,
                    "accounts": [{"company_name": CO, "fixed_asset_account": "Kitchen & Capital Equipment | معدات المطبخ والمعدات الرأسمالية - NJB",
                                  "accumulated_depreciation_account": "Accumulated Depreciation | مجمع الإهلاك - NJB", "depreciation_expense_account": "Depreciation | الإهلاك - NJB"}],
                    "finance_books": [{"depreciation_method": "Straight Line", "total_number_of_depreciations": 60, "frequency_of_depreciation": 1}]}).insert(ignore_permissions=True)
    created("Asset Category", AC)
if not frappe.db.exists("Item", "FA-001"):
    frappe.get_doc({"doctype": "Item", "item_code": "FA-001", "item_name": "Commercial Oven | فرن تجاري", "item_group": IG, "stock_uom": "Nos",
                    "is_stock_item": 0, "is_fixed_asset": 1, "asset_category": AC, "is_sales_item": 0, "include_item_in_manufacturing": 0}).insert(ignore_permissions=True)
    created("Item", "FA-001")
if not frappe.db.exists("Location", LOC):
    frappe.get_doc({"doctype": "Location", "location_name": LOC}).insert(ignore_permissions=True); created("Location", LOC)

LOC2 = "Malqa Kitchen | مطبخ الملقا"
if not frappe.db.exists("Location", LOC2):
    frappe.get_doc({"doctype": "Location", "location_name": LOC2}).insert(ignore_permissions=True); created("Location", LOC2)

# 4. KodeERP sidebar (site layer), grouped like Foodics
def sec(label, icon): return {"type": "Section Break", "label": label, "icon": icon, "collapsible": 1, "child": 0, "added": 1}
def ln(label, lt, to, icon=None, **kw): return {"type": "Link", "label": label, "link_type": lt, "link_to": to, "icon": icon, "child": 1, "collapsible": 1, "added": 1, **kw}
base = {r.get("link_to") or r.get("label"): dict(r) for r in pre["kodeerp_sidebar"] if not r.get("added")}
def ref(to, label=None, icon=None):
    r = dict(base[to]); r.update({"child": 1, "hidden": 0, "added": 0})
    if label: r["label"] = label
    if icon: r["icon"] = icon
    return r
rows = [dict(base["KodeERP Home"], hidden=0, child=0),
  sec("Accounting", "landmark"), ref("Accounting", icon="landmark"), ln("Chart of Accounts", "DocType", "Account", "vault"),
    ln("Journal Entry", "DocType", "Journal Entry", "book-open"), ln("Journal Templates", "DocType", "Journal Entry Template", "copy"),
    ln("Recurring Entries", "DocType", "Auto Repeat", "repeat"), ln("Opening Balances", "DocType", "Opening Invoice Creation Tool", "flag"),
    ln("Cost Centers", "DocType", "Cost Center", "network"), ln("Branches", "DocType", "Branch", "git-branch"),
    ln("Brands", "DocType", "Brand", "award"), ln("Dimensions", "DocType", "Accounting Dimension", "grid-3x3"),
    ln("Budgets", "DocType", "Budget", "piggy-bank"), ln("Lock Periods", "DocType", "Accounting Period", "lock"),
    ln("Period Closing", "DocType", "Period Closing Voucher", "calendar-check-2"),
  sec("Sales", "store"), ref("Customer"), ref("Quotation"), ref("Sales Invoice"),
  sec("Purchasing", "shopping-cart"), ln("Supplier", "DocType", "Supplier", "truck"), ln("Purchase Request", "DocType", "Material Request", "clipboard-pen"), ln("Purchase Order", "DocType", "Purchase Order", "clipboard-list"),
    ln("Purchase Invoice", "DocType", "Purchase Invoice", "receipt"),
  sec("Bank & Cash", "wallet"), ln("Receive / Pay / Transfer", "DocType", "Payment Entry", "wallet"), ln("Bank Account", "DocType", "Bank Account", "landmark"),
    ln("Bank Reconciliation", "DocType", "Bank Reconciliation Tool", "scale"), ln("Bank Transaction", "DocType", "Bank Transaction", "arrow-left-right"),
    ln("Clearance Dates", "DocType", "Bank Clearance", "calendar-check"), ln("Payment Methods & Clearing", "DocType", "Mode of Payment", "credit-card"),
  sec("Inventory", "boxes"), ref("Item"), ln("Warehouses & Kitchens", "DocType", "Warehouse", "warehouse"),
    ln("Recipes", "DocType", "BOM", "chef-hat"), ln("Stock Transfer & Waste", "DocType", "Stock Entry", "arrow-right-left"), ln("Stock Count", "DocType", "Stock Reconciliation", "clipboard-check"),
    ln("Landed Cost", "DocType", "Landed Cost Voucher", "ship"), ln("Cost Repost", "DocType", "Repost Item Valuation", "refresh-cw"),
    ln("Stock Balance", "Report", "Stock Balance", "chart-bar"), ln("Stock Ledger", "Report", "Stock Ledger", "list"), ln("Stock vs Ledger Check", "Report", "Stock and Account Value Comparison", "scale"),
  sec("Assets", "building-2"), ln("Fixed Assets", "DocType", "Asset", "building-2"), ln("Asset Category", "DocType", "Asset Category", "folder"),
    ln("Asset Movement", "DocType", "Asset Movement", "move"), ln("Depreciation Schedules", "DocType", "Asset Depreciation Schedule", "calendar-range"), ln("Fixed Asset Register", "Report", "Fixed Asset Register", "book"),
    ln("Asset Depreciation Ledger", "Report", "Asset Depreciation Ledger", "trending-down"),
  sec("HR & Payroll", "users"), ln("Employees", "DocType", "Employee", "user"), ln("Departments", "DocType", "Department", "building"), ln("Salary Structure", "DocType", "Salary Structure", "layers"),
    ln("Salary Structure Assignment", "DocType", "Salary Structure Assignment", "user-check"), ln("Payroll Run", "DocType", "Payroll Entry", "play"),
    ln("Salary Slip", "DocType", "Salary Slip", "file-text"), ln("Overtime & Bonus", "DocType", "Additional Salary", "clock"),
    ln("Employee Advances", "DocType", "Employee Advance", "hand-coins"), ln("Leave Application", "DocType", "Leave Application", "calendar-x"),
    ln("Holiday List", "DocType", "Holiday List", "calendar"),
  sec("Reports", "chart-column"), ln("Financial Reports", "Workspace", "Financial Reports", "chart-column"),
    ln("General Ledger", "Report", "General Ledger"), ln("Trial Balance", "Report", "Trial Balance"), ln("Profit and Loss", "Report", "Profit and Loss Statement"),
    ln("Balance Sheet", "Report", "Balance Sheet"), ln("Cash Flow", "Report", "Cash Flow"), ln("Profitability Analysis", "Report", "Profitability Analysis"),
    ln("Gross Profit", "Report", "Gross Profit"), ln("Accounts Receivable", "Report", "Accounts Receivable"), ln("Accounts Payable", "Report", "Accounts Payable"),
    ln("Customer Statement", "Report", "Customer Ledger Summary"), ln("Supplier Statement", "Report", "Supplier Ledger Summary"),
    ln("Bank Reconciliation Statement", "Report", "Bank Reconciliation Statement"), ln("Consolidated Financials", "Report", "Consolidated Financial Statement"),
    ln("Budget Variance", "Report", "Budget Variance Report"), ln("Payroll Register", "Report", "Salary Register"),
  sec("VAT & Tax", "percent"), ln("KSA VAT Return (Demo) | إقرار ضريبة القيمة المضافة", "Report", "KSA VAT Return (Demo) | إقرار ضريبة القيمة المضافة", "percent"),
    ln("Sales VAT Template", "DocType", "Sales Taxes and Charges Template", "badge-percent"), ln("Purchase VAT Template", "DocType", "Purchase Taxes and Charges Template", "badge-percent"),
    ln("Item VAT Template", "DocType", "Item Tax Template", "tag"),
  sec("Users & Audit", "shield"), ln("Users", "DocType", "User", "users"), ln("Role Permissions", "Page", "permission-manager", "key-round"),
    ln("Activity Log", "DocType", "Activity Log", "history"),
]
used = {r.get("link_to") for r in rows}
for k, r in base.items():  # hide old sections and the base workspace links not used above
    if r.get("link_to") not in used or r.get("type") == "Section Break":
        rows.append(dict(r, hidden=1))
save_site_sidebar("Kodenova Theme", json.dumps(rows))
# The 3 demo users are not admins: hide the "Users & Audit" group for them (user layer); Administrator keeps it.
from frappe.desk.doctype.custom_sidebar.custom_sidebar import layer_arrangement, _save_customization
ADMIN_ONLY = {"User", "permission-manager", "Activity Log"}
for u in ADD_ROLES:
    arr = layer_arrangement("Kodenova Theme", u)
    for r in arr:
        if r.get("link_to") in ADMIN_ONLY or (r.get("type") == "Section Break" and r.get("label") in ("Users & Audit",)): r["hidden"] = 1
    _save_customization("Kodenova Theme", json.dumps(arr), user=u)

# 5. ar/es labels for the new texts (only the strings we introduced, plus 3 poor stock Arabic ones)
TR = {"Bank & Cash": ("البنك والنقدية", "Banco y caja"), "Inventory": ("المخزون", "Inventario"), "HR & Payroll": ("الموارد البشرية والرواتب", "RR. HH. y nómina"),
 "VAT & Tax": ("ضريبة القيمة المضافة", "IVA e impuestos"), "Users & Audit": ("المستخدمون والتدقيق", "Usuarios y auditoría"),
 "Journal Templates": ("قوالب القيود", "Plantillas de asientos"), "Recurring Entries": ("القيود المتكررة", "Asientos recurrentes"),
 "Opening Balances": ("الأرصدة الافتتاحية", "Saldos iniciales"), "Cost Centers": ("مراكز التكلفة", "Centros de costo"), "Branches": ("الفروع", "Sucursales"),
 "Receive / Pay / Transfer": ("قبض / صرف / تحويل", "Cobros / pagos / transferencias"), "Bank Reconciliation": ("التسوية البنكية", "Conciliación bancaria"),
 "Clearance Dates": ("تواريخ المقاصة", "Fechas de compensación"), "Warehouses & Kitchens": ("المستودعات والمطابخ", "Almacenes y cocinas"),
 "Stock Transfer & Waste": ("تحويل وهدر المخزون", "Traspasos y mermas"), "Stock Count": ("جرد المخزون", "Conteo de inventario"),
 "Landed Cost": ("التكاليف الإضافية للشراء", "Costo en destino"), "Cost Repost": ("إعادة احتساب التكلفة", "Recalcular costo"),
 "Fixed Assets": ("الأصول الثابتة", "Activos fijos"), "Employees": ("الموظفون", "Empleados"), "Payroll Run": ("مسير الرواتب", "Ejecución de nómina"),
 "Salary Slip": ("قسيمة الراتب", "Recibo de nómina"), "Overtime & Bonus": ("العمل الإضافي والمكافآت", "Horas extra y bonos"),
 "Employee Advances": ("سلف الموظفين", "Anticipos a empleados"), "Customer Statement": ("كشف حساب العملاء", "Estado de cuenta de clientes"),
 "Supplier Statement": ("كشف حساب الموردين", "Estado de cuenta de proveedores"), "Payroll Register": ("سجل الرواتب", "Registro de nómina"),
 "Sales VAT Template": ("قالب ضريبة المبيعات", "Plantilla de IVA de ventas"), "Purchase VAT Template": ("قالب ضريبة المشتريات", "Plantilla de IVA de compras"),
 "Role Permissions": ("صلاحيات الأدوار", "Permisos de roles"), "Users": ("المستخدمون", "Usuarios"), "Purchasing": ("المشتريات", "Compras"),
 "Payroll Entry": ("مسير الرواتب", "Ejecución de nómina"), "Employee Advance": ("سلفة موظف", "Anticipo a empleado"),
 "Salary Register": ("سجل الرواتب", "Registro de nómina"),
 "Brands": ("العلامات التجارية", "Marcas"), "Dimensions": ("الأبعاد المحاسبية", "Dimensiones contables"), "Budgets": ("الموازنات", "Presupuestos"),
 "Lock Periods": ("إقفال الفترات", "Bloqueo de periodos"), "Period Closing": ("إقفال السنة المالية", "Cierre del ejercicio"),
 "Purchase Request": ("طلب شراء", "Solicitud de compra"), "Payment Methods & Clearing": ("طرق الدفع وحسابات التسوية", "Medios de pago y compensación"),
 "Recipes": ("الوصفات", "Recetas"), "Stock vs Ledger Check": ("مطابقة المخزون مع الدفاتر", "Inventario vs contabilidad"),
 "Depreciation Schedules": ("جداول الإهلاك", "Calendarios de depreciación"), "Departments": ("الأقسام", "Departamentos"),
 "Consolidated Financials": ("القوائم المالية الموحدة", "Estados financieros consolidados"), "Budget Variance": ("انحراف الموازنة", "Desviación presupuestaria"),
 "Masters": ("البيانات الأساسية", "Maestros"), "Item VAT Template": ("قالب ضريبة الصنف", "Plantilla de IVA por artículo"), "Pending Approval": ("بانتظار الموافقة", "Pendiente de aprobación"),
 "Submit for Approval": ("إرسال للموافقة", "Enviar para aprobación"), "Approve": ("موافقة", "Aprobar"), "Reject": ("رفض", "Rechazar"),
 "Approved": ("معتمد", "Aprobado"), "Rejected": ("مرفوض", "Rechazado"), "Landed Cost Voucher": ("قسيمة التكاليف الإضافية للشراء", "Comprobante de costo en destino")}
for src, (ar, es) in TR.items():
    for lang, txt in (("ar", ar), ("es", es)):
        n = frappe.db.get_value("Translation", {"language": lang, "source_text": src})
        if not n:
            t = frappe.get_doc({"doctype": "Translation", "language": lang, "source_text": src, "translated_text": txt}).insert(ignore_permissions=True)
            pre["translations_created"].append(t.name)

# 6. POS is external (Foodics POS -> accounting): hide POS Invoice from the Accounts sidebar too
acc = get_site_sidebar_layer("Accounts"); pre.setdefault("accounts_sidebar", acc); out = []
for r in pre["accounts_sidebar"]:
    r = dict(r)
    if r.get("type") == "Section Break" and r.get("label") == "Masters & POS": r["label"] = "Masters"; r.pop("key", None)
    if r.get("link_to") == "POS Invoice": continue
    out.append(r)
save_site_sidebar("Accounts", json.dumps(out))

# 7. Extra permissions: BOM (recipes) for Stock Manager, without Manufacturing roles
for role, ptypes in {"Stock Manager": ("read", "write", "create", "submit", "cancel")}.items():
    add_permission("BOM", role, 0)
    for p in ptypes: update_permission_property("BOM", role, 0, p, 1)

# 8. Accounting dimensions Brand + Department, and two demo brands
for bn in ("Najd Bites | نجد بايتس", "Najd Coffee | قهوة نجد"):
    if not frappe.db.exists("Brand", bn): frappe.get_doc({"doctype": "Brand", "brand": bn}).insert(ignore_permissions=True); created("Brand", bn)
for dt in ("Brand", "Department"):
    if not frappe.db.exists("Accounting Dimension", {"document_type": dt}):
        frappe.flags.in_test = True  # build the custom fields now instead of in a background job
        try: frappe.get_doc({"doctype": "Accounting Dimension", "document_type": dt}).insert(ignore_permissions=True)
        finally: frappe.flags.in_test = False
        created("Accounting Dimension", dt)

# 9. Purchase Request approval workflow (Material Request): Stock/Purchase user raises, Accounts Manager approves
for st, style in (("Draft", ""), ("Pending Approval", "Warning"), ("Approved", "Success"), ("Rejected", "Danger"), ("Cancelled", "Inverse")):
    if not frappe.db.exists("Workflow State", st): frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": st, "style": style}).insert(ignore_permissions=True); created("Workflow State", st)
for a in ("Submit for Approval", "Approve", "Reject", "Cancel"):
    if not frappe.db.exists("Workflow Action Master", a): frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": a}).insert(ignore_permissions=True); created("Workflow Action Master", a)
WF = "KodeERP Purchase Request Approval"
if not frappe.db.exists("Workflow", WF):
    frappe.get_doc({"doctype": "Workflow", "workflow_name": WF, "document_type": "Material Request", "is_active": 1, "send_email_alert": 0, "override_status": 0,
        "states": [{"state": "Draft", "doc_status": "0", "allow_edit": "Stock User"}, {"state": "Pending Approval", "doc_status": "0", "allow_edit": "Accounts Manager"},
                   {"state": "Approved", "doc_status": "1", "allow_edit": "Accounts Manager"}, {"state": "Rejected", "doc_status": "0", "allow_edit": "Accounts Manager"},
                   {"state": "Cancelled", "doc_status": "2", "allow_edit": "Accounts Manager"}],
        "transitions": [{"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Approval", "allowed": "Stock User", "allow_self_approval": 1},
                        {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Approval", "allowed": "Purchase User", "allow_self_approval": 1},
                        {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "Accounts Manager", "allow_self_approval": 0},
                        {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Accounts Manager", "allow_self_approval": 0},
                        {"state": "Approved", "action": "Cancel", "next_state": "Cancelled", "allowed": "Accounts Manager", "allow_self_approval": 1}]}).insert(ignore_permissions=True)
    created("Workflow", WF)

# 10. Journal template for daily POS sales imported from the external POS (Foodics) -> accounting
JT = "Daily POS Sales (Foodics) | قيد مبيعات نقاط البيع اليومية"
if not frappe.db.exists("Journal Entry Template", JT):
    frappe.get_doc({"doctype": "Journal Entry Template", "template_title": JT, "company": CO, "voucher_type": "Journal Entry", "naming_series": frappe.get_meta("Journal Entry").get_field("naming_series").options.split("\n")[0],
        "accounts": [{"account": a} for a in ("Foodics POS Clearing | تسوية نقاط البيع فودكس - NJB", "Card & mada Clearing | تسوية مدفوعات البطاقات ومدى - NJB",
                    "Cash on Hand | النقدية في الصندوق - NJB", "Aggregator Receivable Clearing | ذمم تطبيقات التوصيل (تسوية) - NJB", "Dine-in Sales | مبيعات الصالة - NJB",
                    "Takeaway Sales | مبيعات السفري - NJB", "Delivery Sales (Own Fleet) | مبيعات التوصيل الخاص - NJB", "Sales Discounts | الخصومات الممنوحة - NJB",
                    "VAT Output 15% | ضريبة القيمة المضافة - مخرجات 15% - NJB")]}).insert(ignore_permissions=True)
    created("Journal Entry Template", JT)

json.dump(pre, open(STATE, "w"), ensure_ascii=False, indent=1, default=str)
frappe.clear_cache()
print("applied; created", pre["created"])
