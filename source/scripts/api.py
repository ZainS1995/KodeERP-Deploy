#!/usr/bin/env python3
"""Tiny Frappe REST helper for the sandbox. Usage: api.py <site> <METHOD> <path> [json-body]
Logs in as Administrator using .secrets/admin_password (never printed). Cookies cached per site in /tmp."""
import json, os, sys, urllib.request, http.cookiejar
site, method, path = sys.argv[1], sys.argv[2].upper(), sys.argv[3]
body = sys.argv[4] if len(sys.argv) > 4 else None
base = "http://127.0.0.1:8080"
jar_path = f"/tmp/kodeerp-{site}.cookies"
jar = http.cookiejar.MozillaCookieJar(jar_path)
if os.path.exists(jar_path): jar.load(ignore_discard=True)
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def req(m, p, data=None, ctype="application/json"):
    r = urllib.request.Request(base + p, data=data, method=m, headers={"Host": site, "Content-Type": ctype, "Accept": "application/json"})
    try:
        with op.open(r, timeout=600) as resp: return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
st, _ = req("GET", "/api/method/frappe.auth.get_logged_user")
if st != 200:
    pw = open(os.path.join(os.path.dirname(__file__), "..", ".secrets", "admin_password")).read().strip()
    st, out = req("POST", "/api/method/login", json.dumps({"usr": "Administrator", "pwd": pw}).encode())
    if st != 200: print("LOGIN FAILED", st, out[:300]); sys.exit(1)
    jar.save(ignore_discard=True)
st, out = req(method, path, body.encode() if body else None)
try:
    d = json.loads(out)
    if "_server_messages" in d:
        try: d["_server_messages"] = [json.loads(x).get("message", x) for x in json.loads(d["_server_messages"])]
        except Exception: pass
    if "exception" in d or "exc" in d: d.pop("exc", None)
    pick = os.environ.get("PICK")
    if pick and isinstance(d.get("data") or d.get("message"), dict):
        src = d.get("data") or d.get("message"); d = {k: src.get(k) for k in pick.split(",")}
    print(st, json.dumps(d, ensure_ascii=False, indent=1)[:int(os.environ.get("MAXOUT", "2000000"))])
except Exception:
    print(st, out[:2000])
