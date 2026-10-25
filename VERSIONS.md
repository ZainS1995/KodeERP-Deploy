# KodeERP — exact versions (2026-10-21)

| Component | Version | Source / commit |
|---|---|---|
| Frappe Framework | 16.52.0 | github.com/frappe/frappe tag v16.52.0 (4515014c87ec) — from base image |
| ERPNext | 16.51.1 | github.com/frappe/erpnext tag v16.51.1 (5af6561f5aa4) — from base image |
| Frappe HR (hrms) | 16.51.0 | github.com/frappe/hrms tag v16.51.0 (2478afc7a8f4) — cloned at build |
| kodenova_theme | 0.0.1, commit 5a5b239 (2026-10-21) | source/app/kodenova_theme.bundle |
| Base image | frappe/erpnext:v16.51.1 | sha256:85b63c68a1e7992179f5448f334916a49b2e47e5e7382fc346039d073bc7ca27 |
| Python / Node | 3.14.8 / 24.22.0 | in image |
| MariaDB | 11.8 | mariadb:11.8 |
| Redis | 7 | redis:7-alpine |
| Caddy | 2.8 | caddy:2.8-alpine (HTTPS option) |
| cloudflared | 2024.10.0 | cloudflare/cloudflared (tunnel option) |

Installed on both sites: frappe, erpnext, hrms, kodenova_theme.

Not installed on either site and not in the image (present only in the dev bench, under evaluation):
ksa_compliance 0.61.11 (github.com/lavaloon-eg/ksa_compliance, master 91250282f4fe) and
zatca_erpgulf 3.0.1 (github.com/ERPGulf/zatca_erpgulf, main 3f69ce03438). ZATCA e-invoicing is therefore NOT part of this deployment.

Theme changes since the 2026-10-20 package (665ec44 -> 5a5b239): apps screen hides an app tile when the user's
Module Profile blocks every module of that app (F&B accounting users no longer see an empty "People" tile).
Navigation only; permissions unchanged; Administrator unaffected.

fnb site_config setting that is not in the DB backup: `kodeerp_branch_cost_centers` (Branch -> Cost Centre map) —
restore-site.sh copies it from the secrets site_config.json; also in deploy-kit/fnb-branch-cost-centers.json.
