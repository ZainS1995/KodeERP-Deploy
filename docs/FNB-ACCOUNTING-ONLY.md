# F&B demo (fnb.localhost): Foodics-aligned accounting navigation

**Current state (21 Oct 2026, about 8 PM PKT):** the site is organised like Foodics Accounting. One KodeERP sidebar holds the groups **Accounting, Sales, Purchasing, Bank & Cash, Inventory, Assets, HR & Payroll, Reports, VAT & Tax**, plus **Users & Audit**, which only Administrator sees. CRM, Manufacturing, Projects, Support, Quality, Website and Selling/Buying extras (Sales Order, Delivery Note, etc.) stay hidden, and so does **POS**: KodeERP is not the POS, and POS sales arrive as Sales Invoices or daily journals.
This builds on the accounting-only step below. The module profile is unchanged and still blocks every module except Accounts and KodeERP; the new areas are reached through links in the KodeERP sidebar. fnb.localhost only, applied through site records. The one code change is in `kodenova_theme/boot.py` and is noted below.

**Backup taken first:** `sites/fnb.localhost/private/backups/20261021_173416-fnb_localhost-*` (database, files, private files, config).
Scripts: `scripts/fnb_foodics_aligned_apply.py` (idempotent) and `scripts/fnb_foodics_aligned_undo.py`. Pre-state: `docs/fnb-foodics-aligned/fnb_foodics_prestate.json`.
Fit-gap: `/workspace/share/fnb/foodics-aligned/FIT-GAP.md`. Screenshots are in the same folder.

## What changed
| # | Change | Record |
|---|---|---|
| 1 | Roles. EN and AR: + HR User, HR Manager, Expense Approver. Olaya manager: + Purchase User, Stock Manager, HR User. No CRM, Sales Manager, Manufacturing or System Manager roles were added | `Has Role` |
| 2 | Custom DocPerms. Bank Reconciliation Tool: Accounts Manager and Accounts User. Opening Invoice Creation Tool: Accounts Manager. BOM (recipes): Stock Manager create/submit/cancel. Standard rows were copied first | `Custom DocPerm` |
| 3 | KodeERP site sidebar rebuilt into Foodics groups (about 85 links). POS Invoice removed. The old "Daily work" and "Areas" sections and the Selling, Buying and Stock workspace links are hidden | `Custom Sidebar` (Kodenova Theme, site) |
| 4 | User layer for the 3 users hides "Users & Audit" (User, Role Permissions, Activity Log). Administrator still sees it | `Custom Sidebar` (Kodenova Theme, per user) |
| 5 | Accounts sidebar: POS Invoice removed; section "Masters & POS" renamed to "Masters" | `Custom Sidebar` (Accounts, site) |
| 6 | Demo masters (synthetic): Holiday List "KSA Weekends 2026" (Fri/Sat, Founding Day, National Day), assigned to the company (Holiday List Assignment) and set as company default. Salary components Housing Allowance and Overtime; account set on "Basic". Salary Structure "Najd Standard Monthly" (Basic 75%, Housing 25%). Item Group "Fixed Assets", Asset Category "Kitchen Equipment" (straight line, 60 months), item FA-001 "Commercial Oven", Locations "Najd Bites HQ" and "Malqa Kitchen", Brands "Najd Bites" and "Najd Coffee" | various |
| 7 | Account "Salaries Payable" set to account type **Payable** (payroll requires it; the 2 existing journals on it are unaffected) | `Account` |
| 8 | Accounting Dimensions **Brand** and **Department** (adds the brand/department columns on accounting documents and GL) | `Accounting Dimension` + custom fields |
| 9 | Workflow "KodeERP Purchase Request Approval" on Material Request: Draft → (Stock or Purchase User: Submit for Approval) → Pending Approval → (Accounts Manager: Approve → submitted, or Reject). Approved → Cancel. Self-approval is off. Workflow states Draft, Pending Approval and Cancelled and actions Submit for Approval and Cancel were added | `Workflow` |
| 10 | Journal Entry Template "Daily POS Sales (Foodics)": POS, card, cash and aggregator clearing; dine-in, takeaway and delivery sales; discounts; VAT output 15% | `Journal Entry Template` |
| 11 | Demo recipe BOM-MN-001-001 (Chicken Shawarma Sandwich, SAR 4.72), created by the EN test and **kept** | `BOM` |
| 12 | About 57 ar/es Translation rows for the new labels, plus better Arabic for "Inventory", "Salary Register" and "Landed Cost Voucher" | `Translation` |
| 13 | **Code (kodenova_theme, uncommitted):** `boot.py` `_hide_apps_with_no_visible_module` hides an app tile on the apps screen when the user's module profile blocks every module of that app. This removes the "KodeERP People" tile that appeared after the HR roles were added; HR is reached from the KodeERP sidebar. Navigation only; Administrator is not affected | `apps/kodenova_theme/kodenova_theme/boot.py` |

## POS (client decision 21 Oct)
KodeERP is not the POS. POS Invoice and POS Profile have no menu entry anywhere for the 3 users. The Point of Sale page lives in the blocked Selling module, and Home quick actions and number cards have no POS entries (checked). No POS records were deleted; 0 POS Invoices exist, and the 3 POS Profiles and the 150 existing POS-type sales invoices are untouched. As with all module hiding, this is **navigation only**: users with Sales roles could still open /desk/point-of-sale or a POS Invoice by URL or search.
Flow: POS sales become either (a) Sales Invoices to "Walk-in Customer | عميل نقدي" with VAT 15%, paid by method Foodics POS, mada, Card, Cash or Aggregator into the matching clearing account, or (b) a daily journal from the template above. Settlement is an Internal Transfer from clearing to the bank, followed by bank reconciliation. **Limit:** the KSA VAT Return (Demo) report reads invoices only, so POS sales posted as journals are not in it.

## Verification (21 Oct, as each user through the API; all test documents cancelled)
- Boot for all 3 users: only the Accounts and KodeERP sidebars; AR boots in Arabic (RTL) with every group label in Arabic; no "POS", "ERPNext" or "Frappe" text; Spanish labels all translate.
- EN, AR and MG each passed: Quotation, Purchase Order, Stock Count (Stock Reconciliation), Asset (existing asset with depreciation), Employee, Salary Structure Assignment, Salary Slip (6,000 gross, 21 working days), Bank Reconciliation Tool opening plus its balance call, and 11 reports.
- Stock Entry material transfer: EN and AR passed. MG was blocked from the central store by his Olaya-only warehouse permission (by design); his Material Issue (waste) from Olaya Kitchen passed.
- EN only: payroll run (Payroll Entry → slip 8,000 → accrual JE ACC-JV-2026-00106), purchase request → approval (MG blocked from approving) → PO → PI (100% billed), recipe costing and consumption from the recipe, daily POS JE with Brand, walk-in invoice → payment to Foodics clearing → transfer to bank, budget plus Budget Variance, asset depreciation schedule, movement, scrap and restore, accounting-period lock (posting blocked), consolidated, monthly P&L and stock-vs-ledger reports.
- By design for MG: no Payroll Run, Employee Advances or Opening Balances, and he cannot cancel salary slips (Administrator cancelled them).
- Cleanup: all test documents cancelled. Cancelled test salary slips, assignments and 4 test employees deleted. Employee HR-EMP-00005 "QA TEST payroll" is kept as **Left**, because the cancelled payroll run links to it.
- Books: GL 9,560,391.87 Dr = Cr over 2,235 active rows, identical to the baseline. Trial Balance balanced.
- Known: 15 Repost Item Valuation entries are queued and will be processed by the hourly scheduler. The GL is already back to baseline.

## Undo (exact)
```
cd /workspace/kodeerp
cp scripts/fnb_foodics_aligned_undo.py docs/fnb-foodics-aligned/fnb_foodics_prestate.json development/
sudo docker exec -u frappe kodeerp-frappe-1 /workspace/development/run_site_script.sh fnb.localhost /workspace/development/fnb_foodics_aligned_undo.py
(cd development/frappe-bench/apps/kodenova_theme && git checkout kodenova_theme/boot.py)
sudo docker exec -u frappe kodeerp-frappe-1 bash -lc 'cd /workspace/development/frappe-bench && bench --site fnb.localhost clear-cache'
sudo docker exec kodeerp-frappe-1 pkill -HUP -f "gunicorn -b 127.0.0.1:8001" -o
```
The undo restores roles, removes the 3 Custom DocPerm sets, restores both site sidebars, deletes the per-user KodeERP layers, resets the company holiday list, the Salaries Payable type and the Basic component account, cancels the demo recipe, and deletes the created masters, workflow, dimensions and translations. Masters still linked to cancelled test documents (e.g. FA-001, Asset Category, Salary Structure) are disabled instead of deleted. Compile-checked only; **not run**. Last resort: restore the 20261021_173416 backup (destructive: loses later data). After that, the accounting-only undo further below takes the site back to the original state.

## History: first step, accounting-only navigation (still the base layer)

Applied 2026-10-21 ~6:00 PM PKT, **fnb.localhost only** (kodeerp.localhost untouched). Settings/records only: no core or app code changed, no data deleted.

**Backup taken first:** `sites/fnb.localhost/private/backups/20261021_155733-fnb_localhost-*` (database, files, private files, site config).

## What changed (all DB records on fnb)

| # | Change | Record |
|---|---|---|
| 1 | New **Module Profile** `KodeERP Accounting Only (F&B)` blocking all 45 blockable modules except **Accounts** and **Kodenova Theme** (KodeERP Home). Hidden: CRM, Selling, Buying, Stock, Manufacturing, Projects, Support, Quality Management, Assets, all HRMS modules (HR, Payroll, Expenses, Leaves, Recruitment, Shift and Attendance, Performance, Tenure, Tax and Benefits, HR Setup), Setup, Website, Portal, Utilities, Integrations, ERPNext Integrations, Automation, Build, Data, Users, Email, Printing, Contacts, Geo, Regional, Maintenance, Subcontracting, Telephony, Communication, EDI, Bulk Transaction, Workflow, Desk, Custom, Core. | `Module Profile` |
| 2 | That profile set on every enabled non-admin system user (the 3 demo users: najd.accounts.en@, najd.accounts.ar@, najd.olaya.manager@kodeerp.test). Before: no profile, no blocked modules. Administrator is not affected. | `User.module_profile` / `block_modules` |
| 3 | Site-layer sidebar for **KodeERP** (Kodenova Theme): hid Quotation, Selling, Buying, Stock; added Purchase Invoice, POS Invoice, Journal Entry, Supplier, Financial Reports. | `Custom Sidebar` (module Kodenova Theme, user empty) |
| 4 | Site-layer sidebar for **Accounts**: added section "Masters & POS" with Customer, Supplier, Item, Branch*, POS Invoice, KSA VAT Return (Demo). | `Custom Sidebar` (module Accounts, user empty) |
| 5 | User-layer sidebar for each of the 3 users: hid Accounts → Settings (Accounts Settings). Admin still sees it. | `Custom Sidebar` (module Accounts, user = each user) |
| 6 | Quick Actions card "New quotation" on KodeERP Home replaced with "New purchase invoice" (fnb's copy of the block only). | `Custom HTML Block` "KodeERP Quick Actions".html |
| 7 | AR/ES translations for the new texts: Purchases, New purchase invoice, Record a supplier bill with VAT., Input VAT tracked, Branch cost centre, Masters & POS. | `Translation` (12 rows) |

\*Branch is filtered out of the sidebar for these users because their roles have no read permission on Branch (pre-existing; the Branch field on invoices still works).

Scripts: `scripts/fnb_accounting_only_apply.py` (idempotent; saves pre-state), `scripts/fnb_accounting_only_hide_settings.py`. Pre-state: `docs/fnb-accounting-only/prestate.json`.
Then: `bench --site fnb.localhost clear-cache && clear-website-cache`, HUP gunicorn :8001 (tunnels not restarted).

## Not hidden / limits (honest)
- Module blocking is **navigation only** (Frappe design: `is_module_visible` is never a permission check). Documents in hidden modules (e.g. Lead, Quotation, Sales Order) can still be opened by URL or found via the search bar if the user's roles allow. To truly block them, roles would have to be removed (Sales User / Stock User / Purchase User / Stock Manager / Sales Manager) — not done, because Customer/Item/Warehouse/POS flows rely on them.
- Workspaces were **not** set `is_hidden`: that is site-wide (would also hide them from Administrator) and standard workspaces get re-synced on migrate. The module profile covers all non-admin users.
- KodeERP Home keeps the "Stock Value" number card (inventory value is a balance-sheet figure).
- Olaya manager cannot cancel Sales Invoices (pre-existing permission design; open decision for Zain).

## Undo (exact)
```
cd /workspace/kodeerp
cp scripts/fnb_accounting_only_undo.py docs/fnb-accounting-only/prestate.json development/
sudo docker exec -u frappe kodeerp-frappe-1 /workspace/development/run_site_script.sh fnb.localhost /workspace/development/fnb_accounting_only_undo.py
sudo docker exec -u frappe kodeerp-frappe-1 bash -lc 'cd /workspace/development/frappe-bench && bench --site fnb.localhost clear-cache'
sudo docker exec kodeerp-frappe-1 pkill -HUP -f "gunicorn -b 127.0.0.1:8001"
```
The undo script restores each user's module profile/blocked modules from prestate, deletes the 3 user-layer and 2 site-layer Custom Sidebars and the Module Profile, restores the original Quick Actions HTML and deletes the 12 Translation rows. Manual alternative: Desk → User → clear "Module Profile" and unblock modules; delete Custom Sidebar records; delete Module Profile; paste original HTML from prestate.json into Custom HTML Block. Last resort: restore the 20261021_155733 backup (destructive: loses later data). Undo script has not been run (compile-checked only).

## Verification (2026-10-21, local 127.0.0.1:8093 via API, `verify/fnb_accounting_only_test.py`)
- All 3 users: login OK; desk boot has only 2 sidebars (Accounts, KodeERP) — before: 32. AR user boots in Arabic.
- Each user: Sales Invoice insert+submit (cost centre auto from branch), Payment Entry against it, Purchase Invoice insert+submit — all PASS. All marked "QA TEST" and cancelled (SINV 00301–00306, PINV 00043–00045, PAY 00041–00043; manager's SIs cancelled by Administrator).
- Reports open for all 3: General Ledger, Trial Balance, P&L, Balance Sheet, AR, AP, KSA VAT Return (Demo).
- Books back on baseline: GL 9,560,391.87 Dr = Cr, 2,235 active rows; Trial Balance balanced.
- Screenshots: `/workspace/share/fnb/accounting-only/` (en/manager/ar × desk, accounting; en/ar KodeERP Home).
