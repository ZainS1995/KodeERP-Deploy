# KodeERP demo — exact versions (exported 2026-10-20)

| Component | Version | Source / commit |
|---|---|---|
| Frappe Framework | 16.52.0 | github.com/frappe/frappe tag v16.52.0 (bench commit 4515014) |
| ERPNext | 16.51.1 | github.com/frappe/erpnext tag v16.51.1 (5af6561) |
| Frappe HR (hrms) | 16.51.0 | github.com/frappe/hrms tag v16.51.0 (2478afc) |
| kodenova_theme (KodeERP theme) | 0.0.1, commit 665ec44 (2026-10-20) | this package: app/kodenova_theme.bundle |
| Python | 3.14.8 | in image |
| Node.js | 24.22.0 | in image |
| MariaDB | 11.8 | mariadb:11.8 |
| Redis | 7 (alpine) | redis:7-alpine (demo box used redis:alpine) |
| Base image | frappe/erpnext:v16.51.1 | contains frappe 16.52.0 + erpnext 16.51.1 exactly |

Apps installed per site (bench list-apps):
- fnb.localhost: frappe, erpnext, hrms, kodenova_theme
- kodeerp.localhost: frappe, erpnext, hrms, kodenova_theme

Also present in the demo bench but NOT installed on either site (not needed, not shipped):
ksa_compliance 0.61.11, zatca_erpgulf 3.0.1 (ZATCA apps under evaluation).

kodenova_theme 665ec44 adds the line cost centre / Branch sync (item and tax lines follow the header
Cost Center and Branch). Toggle: site_config `kodeerp_sync_line_dimensions` (default on); see
deploy-kit/apps/kodenova_theme/docs/LINE-DIMENSIONS.md.

fnb.localhost settings (Property Setters, in the backup): Branch mandatory on Sales/Purchase Invoice,
Sales Invoice Branch fetched from POS Profile when empty, ignore_user_permissions on Company's
warehouse/cost-centre links and on Sales/Purchase Taxes and Charges cost_center.

kodenova_theme 665ec44 adds: header Cost Centre from Branch. The Branch -> Cost Centre mapping lives in
site_config.json (`kodeerp_branch_cost_centers`), which is NOT part of a bench backup. After restoring
fnb on a new server run:
    bench --site <site> set-config -p kodeerp_branch_cost_centers "$(cat deploy-kit/fnb-branch-cost-centers.json)"
(no mapping = feature inactive; toggle `kodeerp_branch_cost_center_sync`, default on).
