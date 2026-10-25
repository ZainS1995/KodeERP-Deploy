# Temporary public preview

`scripts/preview-start.sh` / `scripts/preview-stop.sh`

- App server: gunicorn (`frappe.app:application`, 2 workers) bound to 127.0.0.1:8001 inside the dev container. It's a production WSGI server with no Werkzeug debugger, and developer_mode is off.
- nginx (`preview/nginx.conf`, run as the box user) on 127.0.0.1:8088 serves /assets and public files from disk and proxies the app and socket.io. It sets `X-Frappe-Site-Name: kodeerp.localhost` so any tunnel hostname maps to the site, and rate-limits POST /api/method/login per client IP (CF-Connecting-IP).
- Cloudflare quick tunnel (`tools/bin/cloudflared`, no account) points ONLY at 127.0.0.1:8088. Sandbox DNS fakes argotunnel.com, so the published edge IPs are pinned with `--edge`.
- The dev server (`bench serve` :8080 with the debugger) and socketio :9010 are never tunnelled; iptables drops non-loopback access to them.
- Hardening applied by `scripts/seed/preview_secure.py`: Administrator password rotated (in .secrets), demo user with no System Manager role, signup disabled, login lockout after 5 failed attempts.
- The quick-tunnel URL changes on every start; it's written to `preview/current-url.txt` (git-ignored).
- To reload Python/hook changes: `sudo docker exec kodeerp-frappe-1 pkill -HUP -f "gunicorn.*8001"`.

## Second preview: F&B demo tenant (fnb.localhost)
`scripts/preview-fnb-start.sh` / `scripts/preview-fnb-stop.sh` run their own nginx (`preview/nginx-fnb.conf`, 127.0.0.1:8093, `X-Frappe-Site-Name: fnb.localhost`) and their own quick tunnel, and reuse the gunicorn on :8001. The URL is written to `preview/fnb-url.txt`. The main demo nginx (:8088) and its tunnel are never touched.
