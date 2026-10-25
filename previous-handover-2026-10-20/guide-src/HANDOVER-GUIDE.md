# KodeERP — Self-Hosting Handover Guide

**Prepared 20 Oct 2026 for Zain (Kodenova).** This guide explains how to run KodeERP (ERPNext v16 + the KodeERP theme) on your own server with your own domain, and how to restore the two demo sites. **We have not deployed anything anywhere and have not changed any DNS.** All steps below are for you (or your admin) to run.

## 0. What is in the package

- `app/` — the KodeERP theme app `kodenova_theme` as a git bundle (full history) and a clean `.tar.gz`.
- `backups/fnb.localhost/` and `backups/kodeerp.localhost/` — fresh backups (database + public files + private files) taken 20 Oct 2026. **Synthetic demo data only.**
- `deploy-kit/` — `Containerfile`, `compose.yaml`, `compose.https.yaml`, `example.env`, `restore-site.sh`.
- `VERSIONS.md` (exact versions), `SHA256SUMS` (checksums). Check them after copying: `sha256sum -c SHA256SUMS`.
- Versions: Frappe 16.52.0, ERPNext 16.51.1, Frappe HR 16.51.0, kodenova_theme 0.0.1 (commit 665ec44). The image is built on the official `frappe/erpnext:v16.51.1` image, which contains exactly Frappe 16.52.0 + ERPNext 16.51.1.
- We tested the kit end to end on our build machine: the image builds, the stack starts, the F&B backup restores with `restore-site.sh`, the KodeERP theme loads (assets `?v=6`), the demo login works, and the list cards API returns the same figures as the demo.

## 1. Decide first

1. **Linux or Windows.** Option A (Ubuntu Server, recommended) is simpler, faster and the standard way to run Frappe. Option B (Windows Server + WSL2 + Docker) works but adds a layer: port forwarding, start-on-boot and updates for WSL.
2. **Demo data or clean start.** The backups are for demos and evaluation. For a real company, create a **new, empty site** (section 5.3) and enter real master data there. Don't run real business on the demo databases.
3. **Domain names**, e.g. `erp.yourdomain.com` (main) and `fnb-demo.yourdomain.com` (F&B demo). Each site is served on its own host name.
4. **Who has admin access** and where off-server backups go (S3, Backblaze, another server).

## 2. Recommended server

| Use | vCPU | RAM | Disk | Notes |
|---|---|---|---|---|
| Demo / up to ~10 users | 2–4 | 8 GB | 80 GB SSD | 4 GB RAM is the bare minimum |
| Small company, 10–30 users | 4 | 16 GB | 160 GB SSD | |
| 30+ users or heavy POS | 8 | 32 GB | 250 GB+ SSD/NVMe | consider a separate DB server |

- Open ports to the internet: **80 and 443 only**. Keep SSH (22) / RDP (3389) limited to your IP addresses or a VPN.
- A static public IP and a domain where you can edit DNS.

## 3. Option A — Ubuntu 22.04 / 24.04 LTS (recommended)

1. Update and add a sudo user: `sudo apt update && sudo apt -y upgrade`.
2. Install Docker Engine + Compose plugin (official docs: docs.docker.com/engine/install/ubuntu): `curl -fsSL https://get.docker.com | sh`, then `sudo usermod -aG docker $USER`, then log out and back in.
3. Copy the package to the server (e.g. `scp -r handover/ user@server:~/`) and check it: `cd ~/handover && sha256sum -c SHA256SUMS`.
4. `cd deploy-kit && cp example.env .env`. Edit `.env` and set a long random `DB_ROOT_PASSWORD` (`openssl rand -hex 24`), `SITE_DOMAIN` and `LETSENCRYPT_EMAIL`.
5. Build the image (5–10 minutes): `docker compose build`.
6. Start: `docker compose up -d`, then `docker compose ps` (everything `running`, `configurator` `exited (0)`).
7. Firewall (UFW): `sudo ufw allow OpenSSH && sudo ufw allow 80,443/tcp && sudo ufw enable`. Docker-published ports bypass UFW, so only publish 80/443 (the HTTPS compose does exactly that). In `compose.yaml` the plain HTTP port 8080 is for testing only.
8. Continue with section 5 (restore) and section 6 (domain and HTTPS).

## 4. Option B — Windows Server via RDP (WSL2 + Docker)

1. Use **Windows Server 2022 (fully updated) or 2025**. On the RDP session, open PowerShell as Administrator: `wsl --install -d Ubuntu-24.04`, then reboot. (If the server is itself a VM, nested virtualisation must be enabled by your host provider.)
2. Inside Ubuntu (WSL), install Docker Engine exactly as in Option A step 2. Docker Desktop also works, but check its licence terms for business use.
3. Enable systemd in WSL: put `[boot]` and `systemd=true` in `/etc/wsl.conf`, then run `wsl --shutdown` in PowerShell and reopen Ubuntu. Run `sudo systemctl enable docker`.
4. **Networking.** On Windows Server 2025 / Windows 11 22H2+, set mirrored mode in `C:\Users\<you>\.wslconfig`: `[wsl2]` and `networkingMode=mirrored`. On Server 2022, forward the ports from Windows to WSL (re-run after each reboot, because the WSL IP changes): `netsh interface portproxy add v4tov4 listenport=443 listenaddress=0.0.0.0 connectport=443 connectaddress=<WSL IP>`, and the same for 80. You get the WSL IP with `wsl hostname -I`.
5. **Start on boot.** Create a Task Scheduler task, trigger *At startup*, run as SYSTEM: `wsl.exe -d Ubuntu-24.04 -u root -- bash -lc "systemctl start docker; cd /home/<user>/handover/deploy-kit && docker compose -f compose.yaml -f compose.https.yaml up -d"`.
6. **Windows Defender Firewall:** allow inbound TCP 80 and 443. Restrict RDP 3389 to your own IPs (Scope tab) or put RDP behind a VPN. Exposed RDP is the most common way these servers get compromised.
7. Keep the package inside the WSL filesystem (`/home/...`), not under `/mnt/c`: it is much faster and avoids permission issues.
8. Then follow Option A steps 3–6 inside Ubuntu, and sections 5–6.

## 5. Restore the demo sites (or create a clean one)

### 5.1 Restore with the script (recommended)

From `deploy-kit/`, with the stack running, choose the final domain as the **site name**. Frappe has no site rename command, so naming the site after its domain from the start avoids renaming later:

`./restore-site.sh fnb-demo.yourdomain.com ../backups/fnb.localhost/*-database.sql.gz ../backups/fnb.localhost/*_localhost-files.tar ../backups/fnb.localhost/*-private-files.tar`

The script asks for a new Administrator password, then: creates the site (with a DB user that the containers can reach), restores the database and files, runs `migrate`, sets the admin password, runs `clear-cache` and `clear-website-cache`, enables the scheduler, and sets `host_name`. Repeat for `kodeerp.localhost` with your main domain.

### 5.2 Manual equivalent

1. `docker compose cp <db.sql.gz> backend:/tmp/db.sql.gz` (also the two `.tar` files).
2. `docker compose exec backend bench new-site <domain> --db-root-password <DB_ROOT_PASSWORD> --admin-password <pw> --mariadb-user-host-login-scope=%`
3. `docker compose exec backend bench --site <domain> restore /tmp/db.sql.gz --with-public-files /tmp/files.tar --with-private-files /tmp/private.tar --db-root-password <DB_ROOT_PASSWORD> --force`
4. `bench --site <domain> migrate`, then `bench build` (only needed if you changed app code; assets are already in the image), then `bench --site <domain> clear-cache`, then `bench --site <domain> enable-scheduler`.

### 5.3 Clean production site (no demo data)

`docker compose exec backend bench new-site erp.yourdomain.com --db-root-password <DB_ROOT_PASSWORD> --admin-password <pw> --mariadb-user-host-login-scope=% --install-app erpnext --install-app hrms --install-app kodenova_theme`. Then open the site and run the setup wizard.

### 5.4 Encryption key (important)

Frappe encrypts stored secrets (email passwords, API secrets) with the site's `encryption_key` in `site_config.json`. **Today neither demo site has an encryption key and no encrypted secrets are stored** (checked 20 Oct 2026), so there is nothing to carry over: the new site creates its own. If someone saves an email account or API secret on the old demo before the move, the key must be copied **before first login** on the new server: `bench --site <domain> set-config encryption_key '<key>'`. We keep the original site configs (with DB credentials) in a private folder on our side. They are not in this package and are not needed for restoring.

## 6. Domain and HTTPS

1. DNS: create an **A record** for each host name (e.g. `erp`, `fnb-demo`) pointing to the server's public IP (and AAAA for IPv6 if you use it). Wait until `nslookup erp.yourdomain.com` returns your IP.
2. In `.env`, set `SITE_DOMAIN` (the host name that Traefik serves) and `LETSENCRYPT_EMAIL`.
3. Start with HTTPS: `docker compose -f compose.yaml -f compose.https.yaml up -d`. Traefik gets a Let's Encrypt certificate automatically (port 80 must be reachable for the HTTP challenge) and redirects HTTP to HTTPS.
4. For **two or more domains**, add each one to the router rule in `compose.https.yaml`, e.g. ``Host(`erp.yourdomain.com`) || Host(`fnb-demo.yourdomain.com`)``. `FRAPPE_SITE_NAME_HEADER=$$host` routes each request to the site with the same name.
5. If you restored under a different name (e.g. `fnb.localhost`), either restore again under the domain name (cleanest), or set `FRAPPE_SITE_NAME_HEADER=fnb.localhost` (single-site only).
6. Set the public URL on each site: `bench --site <domain> set-config host_name https://<domain>` (used in emails and links).
7. Alternative: an existing nginx with certbot in front, proxying to `127.0.0.1:8080`. Pass the `Host` header and the WebSocket upgrade headers (`proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";`).

## 7. Users and passwords — do this right after restoring

- Set a new Administrator password: `bench --site <domain> set-admin-password '<new>'`.
- Change or disable **every demo user**. F&B demo: `najd.accounts.en@kodeerp.test`, `najd.accounts.ar@kodeerp.test`, `najd.olaya.manager@kodeerp.test`. Main demo: `demo@kodeerp.test` and the other `@kodeerp.test` users. Use `bench --site <domain> set-password <user> '<new>'`, or User list → Disabled.
- Create your own named System Manager user, and use the Administrator account only for emergencies.
- Settings → System Settings: set the session expiry, the password policy and the login attempt limits. Turn on two-factor authentication for admins.
- Set up an Email Account (outgoing SMTP) so that password resets and notifications work.

## 8. Scheduler, backups and updates

- **Scheduler:** the `scheduler` container runs the background jobs. Per site: `bench --site <domain> enable-scheduler`, check with `bench --site <domain> doctor`.
- **Backups:** daily cron on the host, e.g. `0 2 * * * cd ~/handover/deploy-kit && docker compose exec -T backend bench --site all backup --with-files`. Backups land in the `sites` volume under `<site>/private/backups`. **Copy them off the server** (rclone/S3), and test a restore every month.
- **Database volume:** never run `docker compose down -v` (`-v` deletes the database volume).
- **Updates:** change the tags in `Containerfile` (base image and `HRMS_REF`), copy in the new theme version, then `docker compose build`, `docker compose up -d`, `docker compose exec backend bench --site all migrate`. Take a backup first and test the update on a copy. Stay on matching major versions (v16 theme with v16 Frappe/ERPNext).
- **OS updates:** Ubuntu `unattended-upgrades`; Windows Update plus `wsl --update`.

## 9. Firewall basics

- Allow inbound 80/443 only. SSH/RDP only from your IPs or a VPN. MariaDB (3306) and Redis are never published: they stay on the internal Docker network.
- Use key-based SSH, disable password SSH login, and install fail2ban (Linux). On Windows, use account lockout and Network Level Authentication for RDP.

## 10. Troubleshooting

| Symptom | Check / fix |
|---|---|
| 404 "Site not found" | The site name must equal the host name in the browser (or set `FRAPPE_SITE_NAME_HEADER`). `docker compose exec backend ls sites` |
| 502 Bad Gateway | Backend not ready: `docker compose logs -f backend`. Wait 1–2 min after start |
| Page without styling / missing theme | `docker compose exec backend bench --site <domain> clear-cache`; restart frontend; check `/assets/kodenova_theme/css/kodeerp_v5.css` returns 200 |
| Restore: "Access denied for user" | Site was created without `--mariadb-user-host-login-scope=%`; use `restore-site.sh` |
| Redis/DB timeouts | `docker compose ps`: db and redis must be running; containers must share the compose network |
| No certificate | DNS not pointing to the server yet, or port 80 blocked; `docker compose logs traefik` |
| Emails not sent / jobs stuck | Scheduler disabled or worker down: `bench --site <domain> doctor`, `docker compose logs queue-short` |
| Real-time updates not working | WebSocket must pass the proxy (Traefik does; for nginx add the Upgrade headers) |
| Windows: site unreachable after reboot | WSL not started or portproxy IP changed — see Option B steps 4–5 |

## 11. Known limitations of the demo

- ZATCA Phase 2 e-invoicing / QR is not active; Foodics sync not connected; some Arabic print labels still English.
- F&B branch manager: the configuration fix (Company's Warehouse/Cost Center link fields ignore user permissions) is applied and included in the fnb backup; the manager creates Olaya invoices/payments and sees Olaya-only reports. Purchase invoices created by the manager currently get no VAT row by default (the purchase VAT template rows use the Head Office cost centre) — select the template or ask us for the matching setting.
