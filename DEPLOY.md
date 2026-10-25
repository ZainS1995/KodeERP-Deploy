# KodeERP — self-hosting guide (for a human and for an AI coding agent)

Package date: 2026-10-21. Two sites are shipped:

| Backup | Company / content | Suggested public name |
|---|---|---|
| `backups/fnb.localhost/20261021_195544-*` | Najd Bites Food Co. (F&B, accounting-only menu, Foodics-aligned) | `fnb.kodenova.com` |
| `backups/kodeerp.localhost/20261021_215547-*` | Main KodeERP demo (6 synthetic companies, en/es/ar) | `erp.kodenova.com` |

All data is synthetic. Secrets (site configs, demo logins) are in the separate **KodeERP-Secrets-2026-10-21.zip**.

> **Agent rules.** Run the steps in order and stop on the first error. Never print `.env`, `site_config.json`
> or `DEMO-LOGINS.txt` contents into logs or chat. Do not rename, remove or "fix" the KodeERP theme
> (`kodenova_theme`): it is what hides upstream product names and logos. Do not add other apps.
> Do not edit files inside `apps/frappe`, `apps/erpnext` or `apps/hrms`.

---

## 0. What you need

- **Server:** Ubuntu 22.04 or 24.04 (VPS, dedicated, or a Linux VM), **4 GB RAM minimum (8 GB recommended)**, 2+ vCPU, 40 GB disk.
  - **Windows RDP server?** Best: create an Ubuntu VM (Hyper-V) and follow this guide inside it.
    Works too: WSL2 Ubuntu with Docker Engine installed inside WSL (or Docker Desktop with the WSL2 backend).
    On Windows/WSL, use **Path B (Cloudflare named tunnel)** — no inbound ports, no Windows port-forwarding,
    survives the public IP changing. WSL must keep running (`wsl --shutdown` stops ERP); set Docker to start on boot.
- **Docker Engine 24+ with Compose v2.24+** (`docker compose version`; `ports: !reset` needs ≥ 2.24).
  Install: `curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER` (log out/in).
- **A domain you control**, e.g. `kodenova.com`, with two hostnames: `erp.kodenova.com` and `fnb.kodenova.com`.
- Internet access from the server to Docker Hub, GitHub (HRMS clone at build time) and Let's Encrypt.

Paths used below: package unzipped to `/opt/kodeerp`, secrets unzipped to `/opt/kodeerp-secrets`.

```bash
sudo mkdir -p /opt/kodeerp /opt/kodeerp-secrets && sudo chown $USER /opt/kodeerp /opt/kodeerp-secrets
unzip KodeERP-Handover-2026-10-21.zip -d /opt/kodeerp          # -> /opt/kodeerp/KodeERP-Handover-2026-10-21/
unzip KodeERP-Secrets-2026-10-21.zip  -d /opt/kodeerp-secrets  # -> /opt/kodeerp-secrets/KodeERP-Secrets-2026-10-21/
chmod -R go-rwx /opt/kodeerp-secrets
cd /opt/kodeerp/KodeERP-Handover-2026-10-21 && sha256sum -c CHECKSUMS.txt     # every line must say OK
chmod +x deploy-kit/*.sh                                        # in case your unzip tool dropped the exec bit
```
(If you received split parts, unzip all parts into the same folder first.)

## 1. DNS

**Path A (Caddy + Let's Encrypt, server has a public IP):** at your DNS provider create
`A  erp  -> <server public IPv4>` and `A  fnb  -> <server public IPv4>` (TTL 300). If DNS is on Cloudflare, set them
to **DNS only (grey cloud)** until the certificate is issued. Check: `dig +short erp.kodenova.com` returns the IP.

**Path B (Cloudflare named tunnel):** the domain must be on Cloudflare. No A records — the tunnel creates CNAMEs (step 4B).

## 2. Firewall

Path A:
```bash
sudo ufw allow OpenSSH && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw allow 443/udp && sudo ufw enable
```
Do **not** open 3306, 6379, 8000, 8080 or 9000. (Docker-published ports bypass ufw — that is why the
Caddy/tunnel overlays un-publish 8080.) On a cloud VPS also allow 80/443 in the provider's security group.
Path B: inbound only SSH/RDP; no web ports needed.

## 3. Configure and build

```bash
cd /opt/kodeerp/KodeERP-Handover-2026-10-21/deploy-kit
cp example.env .env && chmod 600 .env
# edit .env: DB_ROOT_PASSWORD (openssl rand -hex 24), ERP_DOMAIN, FNB_DOMAIN, LETSENCRYPT_EMAIL
# (Path B also CLOUDFLARE_TUNNEL_TOKEN)
docker compose build            # ~5-15 min; image kodeerp:16.51.1-kn2 (~4.7 GB)
```
The image = `frappe/erpnext:v16.51.1` pinned by digest (Frappe 16.52.0 + ERPNext 16.51.1) + HRMS v16.51.0 +
`kodenova_theme` (copied from `deploy-kit/apps/kodenova_theme`, commit 5a5b239). Assets are built into the image.

## 4. Start the stack

**4A — Caddy (HTTPS via Let's Encrypt):**
```bash
docker compose -f compose.yaml -f compose.caddy.yaml up -d
```
**4B — Cloudflare named tunnel (alternative quick path, good for Windows/WSL):**
1. Cloudflare dashboard → Zero Trust → Networks → Tunnels → Create tunnel (cloudflared) → name `kodeerp` → copy the token into `.env` `CLOUDFLARE_TUNNEL_TOKEN=`.
2. In that tunnel add Public Hostnames: `erp.kodenova.com` → `HTTP` `frontend:8080`, and `fnb.kodenova.com` → `HTTP` `frontend:8080`.
3. `docker compose -f compose.yaml -f compose.tunnel.yaml up -d`

This is a *named* tunnel on your own domain: the address never changes (unlike the temporary trycloudflare.com links).

Use the **same `-f` files in every later `docker compose` command** (or `export COMPOSE_FILE=compose.yaml:compose.caddy.yaml`
— or `compose.yaml:compose.tunnel.yaml` — once per shell; the scripts below then pick it up).

Wait until healthy: `docker compose ps` → `configurator` *exited (0)*, everything else *Up*, `db` *healthy*.

## 5. Restore the two sites (site name = public hostname)

```bash
export COMPOSE_FILE=compose.yaml:compose.caddy.yaml     # or compose.yaml:compose.tunnel.yaml
B=../backups; S=/opt/kodeerp-secrets/KodeERP-Secrets-2026-10-21
./restore-site.sh fnb.kodenova.com \
  $B/fnb.localhost/20261021_195544-fnb_localhost-database.sql.gz \
  $B/fnb.localhost/20261021_195544-fnb_localhost-files.tar \
  $B/fnb.localhost/20261021_195544-fnb_localhost-private-files.tar \
  $S/fnb.localhost/site_config.json
./restore-site.sh erp.kodenova.com \
  $B/kodeerp.localhost/20261021_215547-kodeerp_localhost-database.sql.gz \
  $B/kodeerp.localhost/20261021_215547-kodeerp_localhost-files.tar \
  $B/kodeerp.localhost/20261021_215547-kodeerp_localhost-private-files.tar \
  $S/kodeerp.localhost/site_config.json
```
It asks for a new Administrator password (or reads `$ADMIN_PW`). Per site it runs:
`bench new-site --mariadb-user-host-login-scope=%` → `bench restore --with-public-files --with-private-files --force`
→ copies `encryption_key` (if present — it is not, see below) and the `kodeerp_*` settings from the old site_config
→ `bench migrate` → `set-admin-password` → `set-config host_name https://<site>` → `enable-scheduler` → `clear-cache` → `clear-website-cache`.

**encryption_key:** neither demo site has one (checked: 0 encrypted rows), so nothing needs decrypting. If a future
backup's `site_config.json` contains `encryption_key`, the script copies it; manual equivalent:
`docker compose exec backend bench --site <site> set-config encryption_key '<value from old site_config.json>'`.

Manual equivalents of the other steps (all inside `docker compose exec backend ...`):
`bench --site <site> migrate`, `bench build` (only if assets are missing, see Troubleshooting),
`bench --site <site> clear-cache`, `bench --site <site> enable-scheduler`, `bench --site <site> set-config host_name "https://<site>"`.

Restart the app containers once after restoring: `docker compose restart backend websocket queue-short queue-long scheduler frontend`.

## 6. Change passwords (mandatory)

- Change every demo user's password (list in `DEMO-LOGINS.txt` of the secrets zip) via *User → Settings → Change Password*,
  or disable demo users you don't need. Administrator was already set by the script.
- `DB_ROOT_PASSWORD` must be long and random; `.env` must be `chmod 600`.
- Optional: set up outgoing email (*Email Account*) so "Forgot password" works.

## 7. Nightly backups

```bash
sudo mkdir -p /opt/kodeerp-backups && sudo chown $USER /opt/kodeerp-backups
crontab -e
# add (keep COMPOSE_FILE identical to what you started with):
30 2 * * * cd /opt/kodeerp/KodeERP-Handover-2026-10-21/deploy-kit && COMPOSE_FILE=compose.yaml:compose.caddy.yaml ./backup-nightly.sh >> $HOME/kodeerp-backup.log 2>&1
```
`backup-nightly.sh` runs `bench --site all backup --with-files`, copies DB + public + private files + site_config backup of every
site to `/opt/kodeerp-backups/<timestamp>/<site>/`, checks the gzip, keeps 14 days. Copy that folder **off the server** too.

## 8. Upgrades / theme changes

Theme source with full git history: `source/app/kodenova_theme.bundle` (`git clone kodenova_theme.bundle kodenova_theme`).
After changing it: copy to `deploy-kit/apps/kodenova_theme`, `docker compose build`, `docker compose up -d`,
then per site `bench --site <site> migrate && bench --site <site> clear-cache && bench --site <site> clear-website-cache`.
Do not bump frappe/erpnext/hrms versions without testing a restored copy first.

## 9. Verify

1. `https://erp.kodenova.com/login` and `https://fnb.kodenova.com/login` show the **KodeERP** login card (KodeERP logo,
   "Welcome back", square card). Valid padlock (Path A: Let's Encrypt; Path B: Cloudflare).
   No ERPNext/Frappe name or logo anywhere on the login page, browser tab title or desk.
2. Log in as `najd.accounts.en@kodeerp.test` on fnb → lands on the KodeERP home; menu = Accounting, Sales, Purchasing,
   Bank & Cash, Inventory, Assets, HR & Payroll, Reports, VAT; no CRM / POS / Manufacturing / Projects.
3. Accounting → Reports → **Trial Balance**, company *Najd Bites Food Co.*, fiscal year 2026:
   closing debit = closing credit = **9,560,391.87** (2,235 GL rows). Scripted, read-only check:
   ```bash
   docker compose cp verify_fnb.py backend:/tmp/verify_fnb.py
   docker compose exec -T backend bash -c "cd /home/frappe/frappe-bench/sites && /home/frappe/frappe-bench/env/bin/python /tmp/verify_fnb.py fnb.kodenova.com"
   # expect "RESULT": "PASS"
   ```
4. Main site: GL debit = credit = 56,394,275.28 over 1,049 GL rows, 6 synthetic companies.
5. Arabic user `najd.accounts.ar@kodeerp.test` → right-to-left layout.
6. `docker compose logs --tail=50 scheduler queue-short` shows no repeating errors.

## 10. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Page loads unstyled / white, 404 on `/assets/...` | Assets missing or stale: `docker compose exec backend bench build` then `bench --site all clear-cache`, `docker compose restart backend frontend`. Hard refresh the browser (Ctrl+Shift+R). |
| "Site <name> does not exist" / 404 for the whole domain | The site name must equal the hostname you type. `docker compose exec backend ls sites`. Restore again with the exact domain, or set `FRAPPE_SITE_NAME_HEADER=<site>` in .env for a single-site setup. |
| Cloudflare **Error 1033** | Tunnel not connected: `docker compose logs cloudflared`; token wrong/rotated; container stopped. With a named tunnel the hostname stays the same after a restart. |
| Cloudflare 502 / Bad gateway | Public Hostname must point to `http://frontend:8080` (not localhost); `frontend` must be Up. |
| Caddy: no certificate / `acme` errors | DNS A record not pointing here yet, port 80/443 closed, or Cloudflare proxy (orange cloud) on. `docker compose logs caddy`. |
| Redis/DB "Timeout connecting to server" during restore | Containers can't talk to each other — a host firewall is dropping Docker bridge traffic (FORWARD chain). Allow the `kodeerp` bridge or reset the firewall rules; then `docker compose restart`. |
| `Access denied for user` after restore | The site was created without `--mariadb-user-host-login-scope=%`. Drop it (`bench drop-site <site> --db-root-password ... --force`) and rerun restore-site.sh. |
| Login works but realtime/notifications don't | `websocket` container down: `docker compose logs websocket`. |
| Scheduled jobs (emails, depreciation) don't run | `bench --site <site> enable-scheduler`; `scheduler` container Up. |
| `ports: !reset` error | Docker Compose older than 2.24 — upgrade Docker. |
| Branch cost-centre auto-fill doesn't work on fnb | `bench --site fnb.kodenova.com set-config -p kodeerp_branch_cost_centers "$(cat fnb-branch-cost-centers.json)"`. |
| Upstream name/logo visible somewhere | Theme not installed/migrated: `bench --site <site> list-apps` must show `kodenova_theme`; run migrate + clear-cache + clear-website-cache. Report the page, don't patch core. |

## 11. Tested on 2026-10-21 (demo box)

- This exact `Containerfile` built successfully (`kodeerp:16.51.1-kn2`).
- `compose.yaml` stack started (plain HTTP on a test port). The Caddy and tunnel overlays pass `docker compose config` and `caddy validate`, but were **not** run live (no public DNS/domain on the demo box) — the first real certificate/tunnel connection happens on your server.
- `restore-site.sh` restored the fnb backup as `fnb.kodenova.test` and the main backup as `erp.kodenova.test`; migrate OK;
  login page 200 with all 80 referenced assets 200; demo user API login OK; desk title "KodeERP"; no upstream names in visible text;
  `verify_fnb.py` PASS (2,235 rows, 9,560,391.87 both sides); main site 1,049 rows / 56,394,275.28 balanced.
- `backup-nightly.sh` produced a valid backup of the restored site.
- Separately, the fnb backup was restored into a throwaway site on the original dev bench, migrated, and checked the same way. All test sites/volumes were deleted afterwards.
