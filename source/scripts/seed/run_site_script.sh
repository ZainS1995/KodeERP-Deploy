#!/bin/bash
# usage: run_site_script.sh <site> <script.py>  (runs inside container with frappe connected; commits at end)
cd /workspace/development/frappe-bench/sites && ../env/bin/python - "$1" "$2" <<'PY'
import sys, frappe
site, script = sys.argv[1], sys.argv[2]
frappe.init(site=site, sites_path="."); frappe.connect(); frappe.set_user("Administrator")
try:
    exec(compile(open(script).read(), script, "exec"), {"frappe": frappe})
    frappe.db.commit()
finally:
    frappe.destroy()
PY
