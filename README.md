# KodeERP handover package — 2026-10-21

Start with **DEPLOY.md** (written for a human and for an AI coding agent). Nothing here has been deployed and no DNS was changed.
Secrets are NOT in this zip — they are in the separate `KodeERP-Secrets-2026-10-21.zip` (site configs + demo logins).

| Path | What |
|---|---|
| `DEPLOY.md` | Step-by-step production setup: Docker, Caddy + Let's Encrypt or Cloudflare named tunnel, restore, verify, backups, troubleshooting |
| `deploy-kit/` | What runs on the server: `Containerfile` (image: frappe/erpnext v16.51.1 by digest + HRMS v16.51.0 + theme), `compose.yaml` (mariadb 11.8, redis 7, nginx frontend, workers, scheduler, websocket), `compose.caddy.yaml` + `Caddyfile` (HTTPS), `compose.tunnel.yaml` (Cloudflare named tunnel), `example.env`, `restore-site.sh`, `backup-nightly.sh`, `verify_fnb.py`, `fnb-branch-cost-centers.json`, `apps/kodenova_theme` (build context) |
| `backups/fnb.localhost/` | F&B demo (Najd Bites Food Co.) taken 2026-10-21 21:55 PKT, after the accounting-only + Foodics-aligned changes: DB (3.6 MB gz, 910 tables) + public + private files |
| `backups/kodeerp.localhost/` | Main KodeERP demo taken 2026-10-21 21:55 PKT: DB (1.5 MB gz) + public + private files |
| `source/app/` | KodeERP theme app `kodenova_theme`: `kodenova_theme.bundle` (full git history, HEAD 5a5b239) and `kodenova_theme-5a5b239.tar.gz` (clean source) |
| `source/apps.json` | Exact pins (versions, repo URLs, commits) of every app; `apps.bench-original.json` = the dev bench's own file |
| `source/dev-stack/` | Demo-box dev compose (`compose.dev.yml`) and preview nginx configs — reference only, not for production |
| `source/scripts/` | Dev/preview scripts, `fnb_accounting_only_*` and `fnb_foodics_aligned_*` (apply/undo; already applied inside the fnb backup — do NOT re-run on the restored site), seed scripts |
| `source/verify/` | Test scripts + recorded results of the accounting-only / Foodics-aligned changes |
| `docs/` | Design system, FNB-ACCOUNTING-ONLY.md, FIT-GAP.md (Foodics vs KodeERP), setup notes, feature overviews, client test guide, screenshots, restore-test screenshot |
| `previous-handover-2026-10-20/` | The previous package, unchanged (older backups, guide PDF, Traefik-based deploy kit) — kept so nothing is lost |
| `CHECKSUMS.txt` | sha256 of every file (`sha256sum -c CHECKSUMS.txt`) |

The theme (`kodenova_theme`) is what shows KodeERP branding instead of upstream product names — keep it installed.
All business data is synthetic (fictional companies, customers, suppliers, users).
After deploying: change the Administrator password, every demo user password, and use a strong DB root password (DEPLOY.md §6).
