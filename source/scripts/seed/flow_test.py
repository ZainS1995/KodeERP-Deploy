# End-to-end demo flow as each demo user (permission test): Quotation -> SO -> DN -> SI -> Payment.
import frappe
from frappe.utils import nowdate, add_days
from erpnext.selling.doctype.quotation.quotation import make_sales_order
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
CASES = [("demo@kodeerp.test", "Kodenova Demo Trading S.A. (Synthetic)", "Synthetic Cafe Theta (Demo)", ["POS-PRN-80", "POS-SCN-2D", "POS-PAP-80"]),
         ("es.demo@kodeerp.test", "Kodenova Demo Trading S.A. (Synthetic)", "Synthetic Cafe Theta (Demo)", ["POS-PRN-80", "POS-SCN-2D", "POS-PAP-80"]),
         ("ar.demo@kodeerp.test", "شركة كودنوفا للتجارة التجريبية (Demo)", "مقهى الياسمين (تجريبي)", ["AR-POS-PRN", "AR-POS-SCN", "AR-POS-PAP"])]
res = {}
for user, co, cust, items in CASES:
    frappe.set_user(user); step = "quotation"
    try:
        q = frappe.get_doc({"doctype": "Quotation", "quotation_to": "Customer", "party_name": cust, "company": co, "transaction_date": nowdate(),
                            "currency": frappe.get_cached_value("Company", co, "default_currency"), "conversion_rate": 1,
                            "selling_price_list": frappe.db.get_value("Customer", cust, "default_price_list"), "plc_conversion_rate": 1,
                            "taxes_and_charges": frappe.db.get_value("Sales Taxes and Charges Template", {"company": co, "is_default": 1}, "name"),
                            "valid_till": add_days(nowdate(), 15), "items": [{"item_code": i, "qty": 2 if "PAP" not in i else 20,
                            "rate": frappe.db.get_value("Item Price", {"item_code": i, "selling": 1}, "price_list_rate")} for i in items]})
        # same lookup the form does when an item is picked: price list resolved from customer default
        pl = frappe.db.get_value("Customer", cust, "default_price_list")
        q.set_taxes() if hasattr(q, "set_taxes") else None
        if not q.taxes:
            from erpnext.controllers.accounts_controller import get_taxes_and_charges
            q.set("taxes", get_taxes_and_charges("Sales Taxes and Charges Template", q.taxes_and_charges))
        q.insert(); q.submit(); step = "sales order"
        so = make_sales_order(q.name); so.delivery_date = add_days(nowdate(), 3); so.insert(); so.submit(); step = "delivery note"
        dn = make_delivery_note(so.name); dn.insert(); dn.submit(); step = "sales invoice"
        si = make_sales_invoice(dn.name); si.insert(); si.submit(); step = "payment"
        pe = get_payment_entry("Sales Invoice", si.name); pe.reference_no = "SYN-DEMO-" + si.name; pe.reference_date = nowdate(); pe.insert(); pe.submit()
        frappe.db.commit()
        res[user] = {"ok": True, "quotation": q.name, "so": so.name, "dn": dn.name, "si": si.name, "si_status": frappe.db.get_value("Sales Invoice", si.name, "status"),
                     "currency": si.currency, "total": si.grand_total, "taxes": [t.description for t in si.taxes], "pe": pe.name}
    except Exception as e:
        frappe.db.rollback(); res[user] = {"ok": False, "failed_at": step, "error": str(e)[:300]}
    frappe.set_user("Administrator")
for k, v in res.items(): print(k, v)
