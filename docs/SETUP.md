# KodeERP — Local Development / Test Install (box)

Status: **working sandbox**, verified 2026-10-19 (Asia/Karachi). Synthetic data only. Not production.

## 1. Versions chosen and why

| Component | Version | Source |
|---|---|---|
| Frappe Framework | **16.52.0** (branch `version-16`, commit 4515014) | https://github.com/frappe/frappe/tree/version-16 |
| ERPNext | **16.51.1** (branch `version-16`, commit 5af6561) | https://github.com/frappe/erpnext/releases (latest release v16.51.1, 2026-10-15 UTC) |
| Frappe HR (hrms) | **16.51.0** (branch `version-16`, commit 2478afc) | https://github.com/frappe/hrms/releases |
| kodenova_theme | 0.0.1 (local app, git commit f1e2636) | `development/frappe-bench/apps/kodenova_theme` |
| frappe_docker | main @ d84154a (2026-10-19) — its `pwd.yml`/`example.env` pin `frappe/erpnext:v16.51.1` | https://github.com/frappe/frappe_docker |
| Python / Node (in container) | Python 3.14.8, Node 24.22.0 (from `frappe/bench:latest`, bench CLI 5.31.0) | v16 requires `python >=3.14,<3.15`, `node >=24` |
| MariaDB / Redis | `mariadb:11.8`, `redis:alpine` | as in frappe_docker devcontainer example |

**Why v16:** `version-16` is the current stable major (the newest branch on all three repos; there is no `version-17` yet, only `develop`). Both v15 and v16 still receive releases (v15.123.x released the same week), but v16 is what frappe_docker now pins by default and has the longer support runway, so a new product should start on it. `develop` is unstable and is not used. Revisit before production: confirm Frappe's official support window for v15 and v16.

**Why bench-in-Docker and not `pwd.yml`:** the stock `frappe/erpnext` image can't host a custom app we are actively developing (`kodenova_theme`) without a custom image build. The frappe_docker *development* layout (`frappe/bench` image plus MariaDB/Redis containers, bench in a bind-mounted folder) gives a real bench with `bench new-app`, editable apps and backup/restore. We do the production-style image (layered `apps.json` build) later, in the staging stage.

The host has Python 3.13 and Node 20, which are too old for v16. That's another reason to run bench inside the `frappe/bench` container.

## 2. Box facts and deviations from frappe_docker defaults

- Debian 13 (trixie), kernel 6.12, x86_64, 8 vCPU, 15 GiB RAM (≈2–4 GiB free with other agents' browsers running), no swap, 125 GB disk (~107 GB free).
- Docker was not installed. Installed `docker.io 26.1.5` and `docker-compose 2.26.1` from Debian apt. There is no systemd, so `dockerd` is started by hand (`scripts/start.sh` does this).
- **Bridge-network egress is blocked on this box**: legacy iptables has `FORWARD DROP`, plus a sandbox egress proxy. Containers on a bridge network get no DNS or internet. Workaround: every service uses `network_mode: host` and binds to **127.0.0.1** on non-default ports:
  - MariaDB `127.0.0.1:3307`, redis-cache `127.0.0.1:13100`, redis-queue `127.0.0.1:13101`
  - Web (bench serve) `:8080`, socketio `:9010`
- `bench serve` hard-codes `0.0.0.0` and turns on the Werkzeug debugger. `scripts/start.sh` therefore adds iptables rules that DROP ports 8080 and 9010 on any interface except `lo`. These rules don't persist across reboot; start.sh re-adds them.
- `watch` (asset watcher) is commented out in the `Procfile` to save RAM. Run `scripts/bench.sh build --app kodenova_theme` after asset changes, or re-enable it.

## 3. Layout

```
/workspace/kodeerp/
  compose.dev.yml            # mariadb, redis-cache, redis-queue, frappe(bench) — host networking
  .secrets/ (chmod 700)      # admin_password, db_root_password, compose.env — NEVER commit
  development/frappe-bench/  # the bench (apps/, sites/, env/, logs/) — gitignored
  scripts/start.sh stop.sh bench.sh bench-init.sh
  theme-src/                 # source copies of the theme CSS/JS
  docs/SETUP.md              # this file
  verify/login.png           # screenshot of /login with theme included
  frappe_docker/             # upstream clone (reference only, gitignored)
```
`/workspace/kodeerp` is a local git repo (no remote). `.gitignore` excludes `.secrets/`, `development/`, backups and logs. Running `git grep` for both secret values found nothing in the repo.

## 4. Exact commands used (reproduce from scratch)

```bash
# Docker
sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io docker-compose
sudo bash -c 'nohup dockerd > /var/log/dockerd.log 2>&1 &'

# Secrets (generated, never printed)
cd /workspace/kodeerp && mkdir -p .secrets && chmod 700 .secrets && umask 077
python3 -c "import secrets;print(secrets.token_urlsafe(18))" > .secrets/admin_password
python3 -c "import secrets;print(secrets.token_urlsafe(18))" > .secrets/db_root_password
printf 'DB_ROOT_PASSWORD=%s\n' "$(cat .secrets/db_root_password)" > .secrets/compose.env

# Containers
sudo docker compose -p kodeerp -f compose.dev.yml --env-file .secrets/compose.env up -d

# Bench + apps (inside container) — see scripts/bench-init.sh
cp scripts/bench-init.sh development/ && sudo docker exec -u frappe kodeerp-frappe-1 bash -lc 'bash /workspace/development/bench-init.sh'
#   bench init --skip-redis-config-generation --frappe-branch version-16 --python python3.14 frappe-bench
#   bench set-config -g db_host 127.0.0.1; -gp db_port 3307; redis_* -> 127.0.0.1:13100/13101
#   bench set-config -gp webserver_port 8080; -gp socketio_port 9010
#   bench get-app --branch version-16 erpnext ; bench get-app --branch version-16 hrms

# Procfile tweaks
sed -i 's/bench serve  --port 8000/bench serve --port 8080/; s/^watch:/# watch:/' development/frappe-bench/Procfile

# Site
sudo docker exec -u frappe -e ADMIN_PW="$(cat .secrets/admin_password)" -e DBPW="$(cat .secrets/db_root_password)" kodeerp-frappe-1 bash -lc \
 'cd /workspace/development/frappe-bench && bench new-site kodeerp.localhost --db-root-username root --db-root-password "$DBPW" \
  --admin-password "$ADMIN_PW" --mariadb-user-host-login-scope=% --install-app erpnext --install-app hrms && bench use kodeerp.localhost'

# Setup wizard completed via API (synthetic company "Kodenova Demo Trading (Synthetic)", abbr KDT, Pakistan/PKR/Asia/Karachi, FY Jul–Jun)
#   POST /api/method/frappe.desk.page.setup_wizard.setup_wizard.setup_complete  args={...}

# Theme app
printf 'Kodenova Theme\n<desc>\nKodenova\ndev@example.com\nmit\nN\n\n' | sudo docker exec -i -u frappe kodeerp-frappe-1 bash -lc 'cd /workspace/development/frappe-bench && bench new-app kodenova_theme'
#   copy theme-src/*.css,*.js -> apps/kodenova_theme/kodenova_theme/public/{css,js}/
#   hooks.py: app_include_css, app_include_js, web_include_css  -> /assets/kodenova_theme/...
scripts/bench.sh --site kodeerp.localhost install-app kodenova_theme
scripts/stop.sh && scripts/start.sh     # web must restart to import the newly installed app
```

## 5. Start / stop / use

```bash
/workspace/kodeerp/scripts/start.sh        # dockerd (if needed) + containers + bench start; waits for /api/method/ping
/workspace/kodeerp/scripts/stop.sh         # stop bench processes only
/workspace/kodeerp/scripts/stop.sh --all   # also stop containers (volumes/data kept)
/workspace/kodeerp/scripts/bench.sh <args> # any bench command, e.g. --site kodeerp.localhost migrate
```
- URL (from the box only): **http://kodeerp.localhost:8080** (`*.localhost` resolves to 127.0.0.1 in Chrome), or `curl -H "Host: kodeerp.localhost" http://127.0.0.1:8080/...`
- Desk is at `/desk` in v16 (`/app` redirects with 301 to `/desk`).
- User: `Administrator`; password is in `.secrets/admin_password`.
- Restored copy: **http://kodeerp-restore.localhost:8080**
- Logs: `development/frappe-bench/logs/` (`bench-start.log`, `web.log`, `worker.error.log`, …)

## 6. Backup and restore

Back up the site, including files:
```bash
scripts/bench.sh --site kodeerp.localhost backup --with-files
# -> development/frappe-bench/sites/kodeerp.localhost/private/backups/<ts>-kodeerp_localhost-{database.sql.gz,files.tar,private-files.tar,site_config_backup.json}
```
Copy backups off the box before any risky change. They contain DB data; keep them out of git.

Restore into a **new** site (tested 2026-10-19):
```bash
P=/workspace/development/frappe-bench/sites/kodeerp.localhost/private/backups/<ts>-kodeerp_localhost
sudo docker exec -u frappe -e DBPW="$(cat .secrets/db_root_password)" -e ADMIN_PW="$(cat .secrets/admin_password)" kodeerp-frappe-1 bash -lc "
 cd /workspace/development/frappe-bench &&
 bench new-site kodeerp-restore.localhost --db-root-username root --db-root-password \"\$DBPW\" --admin-password \"\$ADMIN_PW\" --mariadb-user-host-login-scope=% &&
 bench --site kodeerp-restore.localhost restore $P-database.sql.gz --with-public-files $P-files.tar --with-private-files $P-private-files.tar \
   --db-root-username root --db-root-password \"\$DBPW\""
```
- **Encryption key:** if the source `site_config.json` has `encryption_key`, copy it to the target site (`bench --site <target> set-config encryption_key '<value>'`), otherwise encrypted fields such as email and integration passwords can't be decrypted. Frappe only creates the key the first time it's needed. On 2026-10-19 the source site didn't have one yet, so nothing needed copying.
- The restore result was checked through the API on the restored site: login OK; Company=2, Customer=1, Item=1, Sales Order=1 (SAL-ORD-2026-00001, 4,500 PKR), same as the source.

Restore **in place**, which overwrites the site (destructive: take a fresh backup first):
```bash
scripts/bench.sh --site kodeerp.localhost restore <db.sql.gz> --with-public-files <files.tar> --with-private-files <private-files.tar> --db-root-username root --db-root-password '<from .secrets>'
scripts/bench.sh --site kodeerp.localhost migrate
```

## 7. Rollback

| Change | Rollback |
|---|---|
| Theme app | `scripts/bench.sh --site kodeerp.localhost uninstall-app kodenova_theme --yes` (then `bench remove-app kodenova_theme` to drop it from the bench); or `git -C development/frappe-bench/apps/kodenova_theme revert <commit>` + restart |
| Bad data / migration | restore the last backup (section 6) |
| App upgrade (`bench update`) | `git -C apps/<app> checkout <previous commit>` → `bench setup requirements` → `bench build` → restore DB backup taken before update → `bench migrate` |
| Whole sandbox | `scripts/stop.sh --all && sudo docker compose -p kodeerp -f compose.dev.yml --env-file .secrets/compose.env down -v && rm -rf development/frappe-bench` (**destroys all data**; re-run section 4) |
| Docker install | `sudo pkill dockerd; sudo apt-get remove docker.io docker-compose` |
| iptables guard | `sudo iptables -D INPUT -p tcp --dport 8080 ! -i lo -j DROP` (same for 9010) |

No Frappe/ERPNext/HRMS core files were modified. Only `Procfile` (a bench file) was edited: web port and watcher.

## 8. Verification log (2026-10-19, Asia/Karachi)

- `GET /login` → 200; `GET /api/method/ping` → 200
- `POST /api/method/login` → `{"message":"Logged In","home_page":"desk"}`; `get_logged_user` → Administrator
- `get_versions` → frappe 16.52.0, erpnext 16.51.1, hrms 16.51.0 (all version-16)
- `GET /api/resource/DocType?filters=[module in Selling,Stock,HR]` → returned DocTypes (Appraisal, Appointment Letter, …)
- Setup wizard via API → `{"status":"ok"}` (17 s)
- REST writes: Company "KodeERP Sandbox Co (Synthetic)" (KSC), Customer "Synthetic Customer Alpha", Item SYN-ITEM-001, Sales Order SAL-ORD-2026-00001 (draft, 3 × 1,500 = 4,500 PKR) all created
- Theme: `/assets/kodenova_theme/css/kodenova_theme.css` → 200 text/css (brand tokens present); JS → 200; `/desk` HTML includes both; `/login` HTML includes the CSS (web_include_css)
- Backup → restore to `kodeerp-restore.localhost` → counts match (see section 6)

## 9. Known limitations / next steps

- The theme is a **placeholder**: tokens plus primary button colour and heading font only. Brand fonts (Inter, Urbanist, DM Mono, Noto Sans Arabic) aren't bundled yet, so the browser falls back to system fonts. Next: self-host the woff2 files under `public/fonts`, logo/favicon via `app_logo_url` and Website Settings, the login page, workspace styling and dark mode.
- Dev mode only: Werkzeug server, `developer_mode` off, no TLS, no nginx/gunicorn. Staging should use a layered frappe_docker image build (`apps.json` with erpnext, hrms, kodenova_theme from a private git repo) plus `compose.yaml` with overrides.
- Memory is tight on the shared box: the stack uses about 1.35 GB (frappe ~0.8 GB, MariaDB ~0.5 GB), and only ~2–4 GB is free because other agents' browsers are running. There's no swap.
- dockerd and the iptables guard don't survive a box reboot; `scripts/start.sh` re-creates both.


## 10. Changes since first write-up and recovery runbook (2026-10-19 evening, Asia/Karachi UTC+5)

- **`default_site` removed** from `sites/common_site_config.json`. With it set, `bench serve` sent every Host to kodeerp.localhost, so other sites (restore test, ZATCA sites) were never really reached. Pick the site with the `Host` header (`http://<site>:8080`, or `curl -H 'Host: <site>' http://127.0.0.1:8080`).
- **Memory warning:** do **not** run a full `bench build` (all apps at once) while the box is busy. On 2026-10-19 it ran the 16 GB box out of memory and the box was reset. Build one app at a time, checking `free -m` first:
  `for a in frappe erpnext hrms kodenova_theme; do scripts/bench.sh build --app $a; done`
- **Recovery after a box reset** (the root FS is reset, so Docker and `/var/lib/docker` with all MariaDB data are gone; `/workspace` persists):
  1. `sudo apt-get install -y docker.io docker-compose` (dockerd is at `/usr/sbin/dockerd`; `scripts/start.sh` adds `/usr/sbin` to PATH and starts it).
  2. Recreate the dirs that the workspace restore dropped: `mkdir -p development/frappe-bench/config/pids apps/hrms/frappe-ui`, then `rm -f development/frappe-bench/config/bench_build.lock`. Without `config/pids`, bench prints "not in bench directory".
  3. Restore files that git tracks but the restore dropped. Paths named `build` were lost, e.g. `cd apps/frappe && git checkout -- frappe/build`. Check with `git status --short | grep '^ D'` in every app.
  4. `scripts/start.sh` (fresh, empty MariaDB).
  5. Restore the site from its backup. Use `bench --site kodeerp.localhost restore <db.sql.gz> --with-public-files <files.tar> --with-private-files <private-files.tar> --db-root-username root --db-root-password "$(cat .secrets/db_root_password)"`, run inside the container.
  6. `scripts/bench.sh setup requirements --node`, then the per-app builds above, then `scripts/bench.sh --site kodeerp.localhost migrate`.
  7. Restart with `scripts/stop.sh && scripts/start.sh`. Re-seed the synthetic data if needed (see below).
- **Backups must leave the volume.** The reset showed that a backup inside the Docker volume is lost with it. The site backup in `sites/<site>/private/backups/` lives on `/workspace` and survived; the MariaDB volume did not. Run `bench backup --with-files` after meaningful changes.
- **Synthetic demo data:** `scripts/seed/seed_demo.py` (copy into `development/` to run) (customers, 3 service items, 9 Sales Invoices dated in FY 2026-27) and `development/seed_rtl.py` (the RTL test user). Run them with `sudo docker exec -u frappe kodeerp-frappe-1 /workspace/development/run_site_script.sh <site> /workspace/development/<script>.py`. The RTL password is read from a temporary 600 file copied from `.secrets/` and deleted afterwards.
- **Helper scripts:** `scripts/api.py <site> <METHOD> <path> [json]` (URL-encode spaces as %20; env `PICK=` limits the fields; Administrator creds come from `.secrets`), `scripts/new-site.sh <site> [apps]`, and `tools/shots/design.mjs` (design screenshot set).
- **Lost in the reset:** the `kodeerp-restore.localhost` DB, which had been restore-verified earlier, and both ZATCA test site DBs. Their site folders remain. The main site was restored from the 20:53 backup and verified.
