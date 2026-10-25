"""Read-only post-restore check for the F&B (Najd Bites) site.
Run inside the backend container, from the bench's sites folder:
    docker compose cp verify_fnb.py backend:/tmp/verify_fnb.py
    docker compose exec -T backend bash -c "cd /home/frappe/frappe-bench/sites && ../env/bin/python /tmp/verify_fnb.py <site>"
Expected for the 2026-10-21 backup: 2,235 GL rows, debit = credit = 9,560,391.87, Trial Balance 2026 closing 9,560,391.87 both sides,
3 najd.* users on module profile "KodeERP Accounting Only (F&B)". Changes nothing."""
import json
import sys

import frappe

EXPECTED = 9560391.87


def main(site):
    frappe.init(site=site, sites_path=".")
    frappe.connect()
    try:
        out = {"site": site}
        rows, dr, cr = frappe.db.sql(
            "select count(*), round(sum(debit),2), round(sum(credit),2) from `tabGL Entry` where is_cancelled=0"
        )[0]
        out.update(gl_rows=rows, gl_debit=float(dr or 0), gl_credit=float(cr or 0))
        from erpnext.accounts.report.trial_balance.trial_balance import execute

        out["trial_balance"] = {}
        for company in frappe.get_all("Company", pluck="name"):
            for fy in frappe.get_all("Fiscal Year", fields=["name", "year_start_date", "year_end_date"]):
                _, data = execute(frappe._dict(company=company, fiscal_year=fy.name, from_date=fy.year_start_date,
                                               to_date=fy.year_end_date, show_zero_values=0))
                tot = [d for d in data if isinstance(d, dict) and "Total" in str(d.get("account") or d.get("account_name") or "")]
                if tot:
                    t = tot[-1]
                    out["trial_balance"][f"{company} / {fy.name}"] = {
                        "closing_debit": round(t.get("closing_debit") or 0, 2),
                        "closing_credit": round(t.get("closing_credit") or 0, 2),
                    }
        out["users"] = frappe.get_all("User", filters={"name": ["like", "najd.%"]}, fields=["name", "enabled", "module_profile"])
        out["installed_apps"] = frappe.get_installed_apps()
        ok = abs(out["gl_debit"] - out["gl_credit"]) < 0.01 and any(
            abs(v["closing_debit"] - EXPECTED) < 0.01 and abs(v["closing_credit"] - EXPECTED) < 0.01
            for v in out["trial_balance"].values())
        out["RESULT"] = "PASS" if ok else "CHECK (totals differ from the 2026-10-21 backup - fine only if new entries were posted)"
        print(json.dumps(out, indent=1, default=str))
    finally:
        frappe.destroy()


if __name__ == "__main__":
    main(sys.argv[1])
