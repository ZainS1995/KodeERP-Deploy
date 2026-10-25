#!/usr/bin/env python3
"""Generate KodeERP dashboard records as app files (standard records + fixtures).

Run from anywhere:  python3 -I tools/gen_dashboards.py
Writes (all synced by `bench migrate`):
  kodenova_theme/kodenova_theme/number_card/<name>/<name>.json        (sync_dashboards)
  kodenova_theme/kodenova_theme/dashboard_chart/<name>/<name>.json    (sync_dashboards)
  kodenova_theme/kodenova_theme/dashboard_chart_source/<name>/...     (sync_for, IMPORTABLE_DOCTYPES)
  kodenova_theme/kodenova_theme/workspace/kodeerp_home/kodeerp_home.json (sync_for)
  kodenova_theme/kodenova_theme/sidebar/kodeerp/kodeerp.json          (sync_for)
  kodenova_theme/fixtures/custom_html_block.json, custom_workspace.json (sync_fixtures: every json in fixtures/)
"""
import json, os, re

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kodenova_theme")
MOD = os.path.join(APP, "kodenova_theme")
MODULE = "Kodenova Theme"
TS = "2026-10-19 23:40:00.000000"
CUR = "PKR"

def scrub(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")

def base(doctype, name):
    return {"doctype": doctype, "name": name, "creation": TS, "modified": TS, "modified_by": "Administrator",
            "owner": "Administrator", "docstatus": 0, "idx": 0}

def std(doctype, folder, name, **kw):
    d = base(doctype, name); d.update(kw)
    write(os.path.join(MOD, folder, scrub(name), scrub(name) + ".json"), d)
    return d

def flt(dt, f, op, v):
    return [dt, f, op, v, False]

# ---------------------------------------------------------------- Number Cards
CARDS = {}
def card(name, dt, fn, field=None, filters=(), color="#0e0e10"):
    CARDS[name] = std("Number Card", "number_card", name, label=name, type="Document Type", document_type=dt,
        function=fn, aggregate_function_based_on=field or "", filters_json=json.dumps(list(filters)),
        dynamic_filters_json=json.dumps([[dt, "company", "=", 'frappe.defaults.get_user_default("Company")']]) if dt in COMPANY_DTS else "[]", is_public=1, is_standard=1, module=MODULE, color=None,  # accent comes from kodeerp_dashboard.css (status colours), number stays ink
       
        show_percentage_stats=0, stats_time_interval="Monthly", currency=None)  # symbol from the company currency field

SI, PI, PE = "Sales Invoice", "Purchase Invoice", "Payment Entry"
COMPANY_DTS = {SI, PI, PE, "Quotation", "Purchase Order", "Delivery Note", "Stock Entry"}
OK, WARN, INK, HL = "#18b26b", "#ff6a3d", "#0e0e10", "#ffd23f"
card("Revenue This Month", SI, "Sum", "base_net_total", [flt(SI,"docstatus","=",1), flt(SI,"posting_date","Timespan","this month")], OK)
card("Outstanding Receivables", SI, "Sum", "outstanding_amount", [flt(SI,"docstatus","=",1), flt(SI,"outstanding_amount",">",0)], WARN)
card("Payables Due", PI, "Sum", "outstanding_amount", [flt(PI,"docstatus","=",1), flt(PI,"outstanding_amount",">",0)], WARN)
card("Stock Value", "Bin", "Sum", "stock_value", [], INK)
CARDS["Stock Value"].update(type="Custom", function="Sum", aggregate_function_based_on="", method="kodenova_theme.api.dashboard.stock_value")
write(os.path.join(MOD, "number_card", "stock_value", "stock_value.json"), CARDS["Stock Value"])
card("New Customers", "Customer", "Count", None, [flt("Customer","creation","Timespan","this month")], HL)
card("Overdue Invoices", SI, "Count", None, [flt(SI,"docstatus","=",1), flt(SI,"status","=","Overdue")], WARN)
card("Cash Received This Month", PE, "Sum", "base_received_amount", [flt(PE,"docstatus","=",1), flt(PE,"payment_type","=","Receive"), flt(PE,"posting_date","Timespan","this month")], OK)
card("Open Quotations", "Quotation", "Count", None, [flt("Quotation","docstatus","=",1), flt("Quotation","status","=","Open")], HL)
card("Purchases This Month", PI, "Sum", "base_net_total", [flt(PI,"docstatus","=",1), flt(PI,"posting_date","Timespan","this month")], INK)
card("Open Purchase Orders", "Purchase Order", "Count", None, [flt("Purchase Order","docstatus","=",1), flt("Purchase Order","status","in",["To Receive and Bill","To Bill","To Receive"])], HL)
card("Overdue Bills", PI, "Count", None, [flt(PI,"docstatus","=",1), flt(PI,"status","=","Overdue")], WARN)
card("Active Stock Items", "Item", "Count", None, [flt("Item","disabled","=",0), flt("Item","is_stock_item","=",1)], INK)
card("Deliveries This Month", "Delivery Note", "Count", None, [flt("Delivery Note","docstatus","=",1), flt("Delivery Note","posting_date","Timespan","this month")], OK)
card("Stock Entries This Month", "Stock Entry", "Count", None, [flt("Stock Entry","docstatus","=",1), flt("Stock Entry","posting_date","Timespan","this month")], INK)

# money cards -> Custom cards with the company currency; count cards -> Custom too (see kodenova_theme/api/dashboard.py MONEY_KPIS)
# every card is Custom: company falls back to the first permitted company (no NULL company filter)
for _n in [n for n in CARDS if n != "Stock Value"]:
    CARDS[_n].update(type="Custom", method="kodenova_theme.api.dashboard." + scrub(_n), filters_json="[]", dynamic_filters_json="[]")
    write(os.path.join(MOD, "number_card", scrub(_n), scrub(_n) + ".json"), CARDS[_n])

# ---------------------------------------------------------------- Chart sources (custom, permission-aware)
SOURCES = {
    "KodeERP Sales Trend": "kodenova_theme.api.dashboard.sales_trend",
    "KodeERP Receivables Ageing": "kodenova_theme.api.dashboard.receivables_ageing",
    "KodeERP Cash Flow": "kodenova_theme.api.dashboard.cash_flow",
}
for name, method in SOURCES.items():
    d = std("Dashboard Chart Source", "dashboard_chart_source", name, source_name=name, module=MODULE, timeseries=0)
    folder = os.path.join(MOD, "dashboard_chart_source", scrub(name))
    if not os.path.exists(os.path.join(folder, "__init__.py")): open(os.path.join(folder, "__init__.py"), "w").close()
    with open(os.path.join(folder, scrub(name) + ".js"), "w") as f:
        f.write(f'''frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["{name}"] = {{
	method: "{method}",
	filters: [
		{{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		}},
	],
}};
''')
for p in [os.path.join(MOD, "dashboard_chart_source", "__init__.py")]:
    open(p, "a").close()

# ---------------------------------------------------------------- Dashboard Charts
CHARTS = {}
def chart(name, **kw):
    kw.setdefault("is_public", 1); kw.setdefault("is_standard", 1); kw.setdefault("module", MODULE)
    kw.setdefault("timespan", "Last Year"); kw.setdefault("time_interval", "Monthly"); kw.setdefault("timeseries", 0)
    kw.setdefault("filters_json", "{}"); kw.setdefault("dynamic_filters_json", "{}"); kw.setdefault("currency", None)  # never hardcode: tooltips use the company / system currency
    kw.setdefault("y_axis", [])
    if kw.get("chart_type") == "Custom":
        opts = json.loads(kw.get("custom_options") or "{}"); opts.setdefault("fieldtype", "Float")  # no symbol: values are in the user company currency; kw["custom_options"] = json.dumps(opts); kw.setdefault("roles", [])
    CHARTS[name] = std("Dashboard Chart", "dashboard_chart", name, chart_name=name, **kw)

AX = {"xAxisMode": "tick", "shortenYAxisNumbers": 1}
chart("Sales Trend", chart_type="Custom", document_type=SI, source="KodeERP Sales Trend", type="Bar",
      custom_options=json.dumps({"type": "axis-mixed", "colors": ["#dcdce1", "#f5b800"], "height": 260,
          "barOptions": {"spaceRatio": 0.45}, "lineOptions": {"dotSize": 5, "regionFill": 0, "spline": 1},
          "axisOptions": AX}),
      empty_state_message="No sales invoices in the last 6 months yet.")
chart("Top Customers by Sales", chart_type="Group By", document_type=SI, group_by_type="Sum", group_by_based_on="customer",
      aggregate_function_based_on="base_net_total", number_of_groups=5, type="Donut",
      filters_json=json.dumps([flt(SI, "docstatus", "=", 1)]),
      custom_options=json.dumps({"colors": ["#0e0e10", "#ffd23f", "#ff6a3d", "#18b26b", "#cfd0d6", "#6c6c74"], "height": 260}),
      empty_state_message="Top customers appear after your first invoices.")
chart("Receivables Ageing", chart_type="Custom", document_type=SI, source="KodeERP Receivables Ageing", type="Bar",
      custom_options=json.dumps({"colors": ["#ff6a3d"], "height": 260, "barOptions": {"spaceRatio": 0.5}, "axisOptions": AX}),
      empty_state_message="Nothing outstanding. Every invoice is paid.")
chart("Cash In vs Out", chart_type="Custom", document_type=PE, source="KodeERP Cash Flow", type="Bar",
      custom_options=json.dumps({"colors": ["#18b26b", "#ff6a3d"], "height": 260, "barOptions": {"spaceRatio": 0.4}, "axisOptions": AX}),
      empty_state_message="No payments recorded in the last 6 months.")
chart("Purchase Trend", chart_type="Sum", document_type=PI, based_on="posting_date", value_based_on="base_net_total",
      timespan="Last Quarter", time_interval="Monthly", timeseries=1, type="Bar",
      filters_json=json.dumps([flt(PI, "docstatus", "=", 1)]),
      custom_options=json.dumps({"colors": ["#0e0e10"], "height": 260, "barOptions": {"spaceRatio": 0.5}}),
      empty_state_message="No purchase invoices this quarter.")
chart("Stock Value by Warehouse", chart_type="Custom", document_type="Bin", source="Warehouse wise Stock Value", type="Bar",
      custom_options=json.dumps({"colors": ["#0e0e10"], "height": 260, "barOptions": {"spaceRatio": 1.6}}),
      empty_state_message="No stock on hand yet.")

# ---------------------------------------------------------------- Workspace blocks helpers
_bid = [0]
def bid():
    _bid[0] += 1; return f"kd{_bid[0]:08d}"
def b(t, name=None, col=12, **data):
    d = {"col": col}; d.update(data)
    if name is not None: d[t + "_name"] = name
    return {"id": bid(), "type": t, "data": d}
def head(text):
    return {"id": bid(), "type": "header", "data": {"text": f'<span class="h4"><b>{text}</b></span>', "col": 12}}

# ---------------------------------------------------------------- Custom HTML Blocks (fixtures)
CSS_LINK = '@import url("/assets/kodenova_theme/css/kodeerp_dashboard.css");'
CHECK = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9"/><path d="M6 10.2l2.6 2.6L14 7.4"/></svg>'
GREETING_HTML = f'''<section class="kd-hero" aria-label="Overview">
  <div class="kd-eyebrow"><span class="kd-company" data-i18n>Overview</span></div>
  <h1 class="kd-h1"><span class="kd-greet" data-i18n>Welcome back</span>, <span class="hl kd-name" data-i18n>there</span></h1>
  <p class="kd-sub" data-i18n>Here is how the business is doing today: sales, cash, receivables and stock in one place.</p>
  <div class="kd-chips">
    <span class="kd-chip kd-chip-ok">{CHECK}<span class="kd-date" data-i18n>Today</span></span>
    <span class="kd-chip" data-i18n>Synthetic demo data</span>
  </div>
</section>'''
GREETING_JS = r'''const r = root_element;
r.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = __(el.textContent.trim()); });
r.querySelector(".kd-hero").setAttribute("aria-label", __("Overview"));
const first = (frappe.boot.user && frappe.boot.user.first_name) || (frappe.session.user_fullname || "").split(" ")[0] || __("there");
const h = new Date().getHours();
r.querySelector(".kd-greet").textContent = h < 12 ? __("Good morning") : h < 17 ? __("Good afternoon") : __("Good evening");
r.querySelector(".kd-name").textContent = first;
const co = frappe.defaults.get_user_default("Company");
if (co) r.querySelector(".kd-company").textContent = co;
try {
  r.querySelector(".kd-date").textContent = new Intl.DateTimeFormat(frappe.boot.lang || "en", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
} catch (e) {}'''

ICONS = {
    "invoice": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h9l3 3v15l-2.5-1.5L13 21l-2.5-1.5L8 21l-2-1.2V3z"/><path d="M9 9h6M9 13h6M9 17h3"/></svg>',
    "quote": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
    "pay": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="6" width="18" height="12" rx="3"/><circle cx="12" cy="12" r="2.6"/><path d="M7 9.5v5M17 9.5v5"/></svg>',
    "item": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/></svg>',
}
ACTIONS = [
    ("Sales Invoice", "invoice", "New invoice", "Bill a customer in under a minute.", "Sales", ["Branded print layout", "Shares as PDF"], True, "{}"),
    ("Quotation", "quote", "New quotation", "Send prices and convert to an order later.", "Sales", ["Reusable items", "One-click to order"], False, "{}"),
    ("Payment Entry", "pay", "Receive payment", "Record money in and clear open invoices.", "Cash", ["Auto-allocates", "Bank or cash"], False, '{"payment_type":"Receive","party_type":"Customer"}'),
    ("Item", "item", "New item", "Add a product or service to sell or stock.", "Stock", ["Price and stock", "Barcode ready"], False, "{}"),
]
qa = ['<section class="kd-qa" aria-label="Quick actions">']
for dt, ic, title, desc, tag, checks, primary, opts in ACTIONS:
    lis = "".join(f"<li>{CHECK}<span data-i18n>{c}</span></li>" for c in checks)
    btn_cls = "kd-btn kd-btn-primary" if primary else "kd-btn kd-btn-ghost"
    qa.append(f'''  <article class="kd-plan" data-doctype="{dt}" data-opts='{opts}'>
    <span class="kd-badge">{ICONS[ic]}</span>
    <span class="kd-tag" data-i18n>{tag}</span>
    <h3 data-i18n>{title}</h3>
    <p data-i18n>{desc}</p>
    <ul class="kd-check">{lis}</ul>
    <button type="button" class="{btn_cls}"><span data-i18n>{title}</span><span class="kd-arrow" aria-hidden="true">&rarr;</span></button>
  </article>''')
qa.append("</section>")
QA_HTML = "\n".join(qa)
QA_JS = r'''const r = root_element;
r.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = __(el.textContent.trim()); });
r.querySelector(".kd-qa").setAttribute("aria-label", __("Quick actions"));
r.querySelectorAll(".kd-plan").forEach((card) => {
  const dt = card.dataset.doctype;
  if (frappe.model && frappe.model.can_create && !frappe.model.can_create(dt)) { card.remove(); return; }
  const go = () => frappe.new_doc(dt, JSON.parse(card.dataset.opts || "{}"));
  card.querySelector("button").addEventListener("click", (e) => { e.stopPropagation(); go(); });
  card.addEventListener("click", go);
});
if (!r.querySelector(".kd-plan")) r.querySelector(".kd-qa").remove();'''

def html_block(name, html, js):
    d = base("Custom HTML Block", name)
    d.update({"html": html, "script": js, "style": CSS_LINK, "private": 0, "roles": []})
    return d
BLOCKS = [html_block("KodeERP Greeting", GREETING_HTML, GREETING_JS), html_block("KodeERP Quick Actions", QA_HTML, QA_JS)]
write(os.path.join(APP, "fixtures", "custom_html_block.json"), BLOCKS)

# ---------------------------------------------------------------- KodeERP Home workspace
# quick_list_filter uses 4-element filters: frappe.utils.cleanup_filters drops the last filter when they have 5
QL = [
    {"document_type": SI, "label": "Recent Invoices", "quick_list_filter": json.dumps([[SI, "docstatus", "=", 1]])},
    {"document_type": SI, "label": "Overdue Invoices", "quick_list_filter": json.dumps([[SI, "status", "=", "Overdue"]])},
]
home_cards = ["Revenue This Month", "Outstanding Receivables", "Payables Due", "Stock Value", "New Customers", "Overdue Invoices"]
home_charts = ["Sales Trend", "Top Customers by Sales", "Receivables Ageing", "Cash In vs Out"]
content = [b("custom_block", "KodeERP Greeting")]
content += [b("number_card", n, 4) for n in home_cards]
content += [head("Quick actions"), b("custom_block", "KodeERP Quick Actions")]
content += [head("Performance")] + [b("chart", n, 6) for n in home_charts]
content += [head("Invoices")] + [b("quick_list", q["label"], 6) for q in QL]
ws = std("Workspace", "workspace", "KodeERP Home", label="KodeERP Home", title="KodeERP Home", module=MODULE,
    public=1, standard=1, is_hidden=0, hide_custom=1, icon="house", indicator_color="", sequence_id=0.5,
    for_user="", parent_page="", restrict_to_domain="", type="Workspace", link_type="", link_to="", external_link="",
    content=json.dumps(content),
    number_cards=[{"number_card_name": n, "label": n} for n in home_cards],
    charts=[{"chart_name": n, "label": n} for n in home_charts],
    custom_blocks=[{"custom_block_name": n, "label": n} for n in ["KodeERP Greeting", "KodeERP Quick Actions"]],
    quick_lists=QL, shortcuts=[], links=[], roles=[])

# ---------------------------------------------------------------- KodeERP sidebar (desk shell for the home)
def si(label, lt, to, icon, **kw):
    d = {"type": "Link", "label": label, "link_type": lt, "link_to": to, "icon": icon, "child": 0, "indent": 0,
         "collapsible": 1, "keep_closed": 0, "show_arrow": 0, "open_in_new_tab": 0, "hidden": 0, "added": 0,
         "is_default_module": 0}
    d.update(kw); return d
items = [si("Home", "Workspace", "KodeERP Home", "house"),
         {"type": "Section Break", "label": "Daily work", "child": 0, "indent": 0, "collapsible": 1, "keep_closed": 0, "hidden": 0, "added": 0, "show_arrow": 0, "open_in_new_tab": 0, "is_default_module": 0},
         si("Sales Invoice", "DocType", "Sales Invoice", "receipt-text", child=1),
         si("Quotation", "DocType", "Quotation", "file-text", child=1),
         si("Payment Entry", "DocType", "Payment Entry", "wallet", child=1),
         si("Customer", "DocType", "Customer", "user-round", child=1),
         si("Item", "DocType", "Item", "package", child=1),
         {"type": "Section Break", "label": "Areas", "child": 0, "indent": 0, "collapsible": 1, "keep_closed": 0, "hidden": 0, "added": 0, "show_arrow": 0, "open_in_new_tab": 0, "is_default_module": 0},
         si("Accounting", "Workspace", "Accounting", "landmark", child=1),
         si("Selling", "Workspace", "Selling", "store", child=1),
         si("Buying", "Workspace", "Buying", "shopping-cart", child=1),
         si("Stock", "Workspace", "Stock", "boxes", child=1)]
for i, it in enumerate(items, 1):
    it.update({"doctype": "Sidebar Item", "idx": i, "parentfield": "items", "parenttype": "Sidebar"})
std("Sidebar", "sidebar", "KodeERP", title="KodeERP", module=MODULE, app="kodenova_theme", header_icon="house",
    standard=1, items=items, merged_from=None)

# ---------------------------------------------------------------- Custom Workspace snapshots for standard workspaces
def custom_ws(ws_name, cards, charts, keep_cards, cols_card=3):
    content = [b("number_card", n, cols_card) for n in cards]
    content += [b("chart", c, col) for c, col in charts]
    content += [head("Reports & tools")] + [b("card", c, 4) for c in keep_cards]
    widgets = {"number_card": [{"number_card_name": n, "label": n} for n in cards],
               "chart": [{"chart_name": c, "label": c} for c, _ in charts]}
    d = base("Custom Workspace", ws_name)
    d.update({"workspace": ws_name, "visibility": "Inherit", "content": json.dumps(content), "widgets": json.dumps(widgets),
              "override_sequence": 0, "sequence_id": 0, "added_roles": [], "removed_roles": [], "icon": None, "indicator_color": None})
    return d
CW = [
    custom_ws("Accounting", ["Revenue This Month", "Cash Received This Month", "Outstanding Receivables", "Payables Due"],
              [("Cash In vs Out", 6), ("Receivables Ageing", 6)],
              ["Financial Statements", "Receivables & Payables", "Invoicing & Payments", "Banking", "Tax & Compliance", "Registers & Profitability"]),
    custom_ws("Selling", ["Revenue This Month", "Open Quotations", "Overdue Invoices", "New Customers"],
              [("Sales Trend", 7), ("Top Customers by Sales", 5)],
              ["Sales Reports", "Customer Reports", "Pricing"]),
    custom_ws("Buying", ["Purchases This Month", "Payables Due", "Open Purchase Orders", "Overdue Bills"],
              [("Purchase Trend", 12)],
              ["Purchase Reports", "Order Status Reports", "Supplier Reports"]),
    custom_ws("Stock", ["Stock Value", "Active Stock Items", "Deliveries This Month", "Stock Entries This Month"],
              [("Stock Value by Warehouse", 12)],
              ["Stock Reports", "Movement Reports", "Item Reports", "Tools"]),
]
write(os.path.join(APP, "fixtures", "custom_workspace.json"), CW)
for d in ["", "number_card", "dashboard_chart", "workspace", "sidebar"]:
    p = os.path.join(MOD, d, "__init__.py")
    if os.path.isdir(os.path.dirname(p)): open(p, "a").close()
print("ok", len(CARDS), "cards", len(CHARTS), "charts")
