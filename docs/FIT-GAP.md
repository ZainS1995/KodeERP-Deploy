# Foodics Accounting vs KodeERP F&B demo (fnb.localhost): fit-gap

Updated on 21 Oct 2026 at about 8:00 PM PKT. The tests ran through the API as the demo users on 127.0.0.1:8093, and every test document was cancelled afterwards.
Test scripts: `/workspace/kodeerp/verify/fnb_foodics_aligned_test*.py`. Results: `verify/fnb_foodics_aligned_result*.json`.
Users: **EN** = najd.accounts.en, **AR** = najd.accounts.ar, **MG** = najd.olaya.manager (Olaya only).

Legend: **A-T** = Available and tested · **A-NT** = Available, not tested end-to-end · **N/A** = Not available (or not set up on this site)

| # | Foodics capability | KodeERP (sidebar group → entry) | Status | Evidence / note |
|---|---|---|---|---|
| 1 | Chart of accounts, journals | Accounting → Chart of Accounts, Journal Entry | A-T | JE tested by EN (daily POS sales JE; earlier accrual tests) |
| 1 | Opening balances | Accounting → Opening Balances (Opening Invoice Creation Tool); JE "Is Opening" | A-NT | The tool opens for EN/AR (Accounts Manager). MG is not given access by design |
| 1 | Recurring journals | Accounting → Recurring Entries (Auto Repeat), Journal Templates | A-NT | Lists open for all 3 users. Template "Daily POS Sales (Foodics)" was created |
| 1 | Cost centres / branches | Accounting → Cost Centers, Branches | A-T | Every test invoice and JE carried a branch and cost centre |
| 1 | Period closing / lock | Accounting → Lock Periods (Accounting Period), Period Closing | A-T (lock) / A-NT (closing) | EN locked Jan 2025 and posting into it was blocked, then the lock was deleted. No year-end Period Closing Voucher was posted (it would close the 2026 books). Note: inserting an Accounting Period through the API without explicit rows fails (an upstream bug). The form fills the rows |
| 2 | Customers, quotations | Sales → Customer, Quotation | A-T | Quotation insert, submit and cancel: EN, AR, MG |
| 2 | Sales invoices, credit notes | Sales → Sales Invoice (Create → Return) | A-T (invoice) / A-NT (credit note) | Walk-in invoice with VAT 15% by EN. Credit note not re-tested today |
| 2 | AR reports | Reports → Accounts Receivable, Customer Statement | A-T | All 3 users |
| 3 | Suppliers, purchase orders, purchase invoices | Purchasing → Supplier, Purchase Order, Purchase Invoice | A-T | PO by EN, AR and MG. PI from PO by EN |
| 3 | Purchase request + approval | Purchasing → Purchase Request (Material Request + workflow "KodeERP Purchase Request Approval") | A-T | MG raised the request and sent it for approval. MG was blocked from approving it. EN approved it, then created the PO and the PI from that PO |
| 3 | PO-to-invoice matching | PO billed % / request ordered % | A-T | PO per_billed = 100 and MR per_ordered = 100 |
| 3 | Debit/credit notes, supplier payments, AP reports | Purchase Invoice → Return; Receive/Pay/Transfer; Accounts Payable, Supplier Statement | A-T (AP, payments) / A-NT (debit note) | |
| 4 | Bank accounts, receive / pay / transfer | Bank & Cash → Bank Account, Receive / Pay / Transfer | A-T | Payment into the Foodics clearing account, then an Internal Transfer from clearing to the bank (EN) |
| 4 | Payment clearing accounts | Bank & Cash → Payment Methods & Clearing | A-T | Foodics POS, mada, Card and Aggregator each map to their own clearing account |
| 4 | Bank reconciliation | Bank & Cash → Bank Reconciliation, Clearance Dates, Bank Transaction; Reports → Bank Reconciliation Statement | A-T (opens and balance call) | Opens for all 3 users. No bank statement was imported (no bank feeds) |
| 4 | Cash control | Cash on Hand / Petty Cash accounts, Internal Transfer | A-NT | |
| 5 | Employees (branch), departments | HR & Payroll → Employees, Departments | A-T | Employee created by EN, AR and MG |
| 5 | Salary, payroll runs | Salary Structure, Assignment, Payroll Run, Salary Slip | A-T | Salary slips by all 3 users: gross 6,000, 21 working days. EN ran a full payroll run: slip 8,000, accrual JE 8,000, then cancelled |
| 5 | Overtime / bonus | Overtime & Bonus (Additional Salary), component "Overtime" | A-NT | The list opens. The component was created |
| 5 | Employee loans / advances with deduction | Employee Advances (salary deduction option) | A-NT | EN and AR only (MG is not given access by design) |
| 5 | Leave and holidays | Leave Application, Holiday List (KSA Weekends 2026, assigned to the company) | A-T (holidays) / A-NT (leave) | |
| 5 | Benefits (GOSI etc.) | Accounts exist (GOSI payable/expense) | A-NT | GOSI is not configured as a salary component |
| 6 | Stock transfers | Inventory → Stock Transfer & Waste | A-T | EN and AR moved stock from the central store to a kitchen. MG's transfer was blocked because MG may only use the Olaya warehouse (by design) |
| 6 | Waste / spoilage | Stock Entry Material Issue → Wastage & Spoilage | A-T | MG, from the Olaya kitchen |
| 6 | Stock counts | Inventory → Stock Count | A-T | All 3 users |
| 6 | Recipe costing | Inventory → Recipes (BOM; Stock Manager given BOM rights without Manufacturing roles) | A-T | Demo recipe BOM-MN-001-001 (Chicken Shawarma Sandwich) costs SAR 4.72 and was **kept** as demo data |
| 6 | Ingredient consumption | Material Issue "From BOM" | A-T | 10 sandwiches → 1.5 kg chicken, 10 bread, 0.2 kg tahini, 0.1 kg garlic = SAR 47.22, then cancelled. Consumption is not deducted automatically by each sale |
| 6 | Returns, landed cost, cost repost | Purchase/Sales returns, Landed Cost, Cost Repost | A-NT | The lists open |
| 6 | Stock valuation | Stock Balance, Stock Ledger, Stock vs Ledger Check | A-T | Reports ran |
| 7 | Fixed asset register, depreciation | Assets → Fixed Assets, Depreciation Schedules, Fixed Asset Register, Depreciation Ledger | A-T | Assets by all 3 users. The schedule has 61 rows (a part-month first row plus 60 months) |
| 7 | Asset transfer | Assets → Asset Movement | A-T | HQ → Malqa Kitchen (EN) |
| 7 | Asset disposal | Asset → Scrap / Restore | A-T | Scrap posted the disposal JE and a 1-day depreciation. Restore and cancel brought them back to zero |
| 7 | Loans (bank / lending) | — | N/A | No loan module is installed. Use loan liability accounts and journals |
| 8 | Balance sheet, P&L (detailed / monthly), cash flow | Reports | A-T | |
| 8 | Profitability, gross profit | Reports → Profitability Analysis, Gross Profit | A-T | |
| 8 | Consolidated financials | Reports → Consolidated Financials | A-T | Runs (single company) |
| 8 | Budgets + variance | Accounting → Budgets; Reports → Budget Variance | A-T | Budget created by EN, report ran, budget cancelled |
| 8 | Statement of changes in equity | — | N/A | No standard report. Equity movements show in the Balance Sheet and GL |
| 8 | Financial dimensions: branch, brand, department, cost centre | Accounting Dimensions Branch (existing), **Brand** and **Department** (new) | A-T (branch, brand, cost centre) / A-NT (department) | JE with Brand "Najd Bites"; GL filtered by brand |
| 9 | Saudi VAT report | VAT & Tax → KSA VAT Return (Demo); VAT templates | A-T (runs) | It reads Sales/Purchase **Invoices** only, so POS sales posted as journals do not appear in it |
| 9 | ZATCA e-invoicing | — | N/A on this site | The ksa_compliance and zatca_erpgulf apps exist on the bench but are **not installed on fnb.localhost**. Not configured; no credentials; no ZATCA endpoint was called |
| 9 | Zakat | Zakat & Tax Expense account only | N/A | No built-in Zakat return or Zakat-base report |
| 9 | User roles and permissions | Users & Audit (Administrator only) | A-NT | Hidden from the 3 demo users |
| 9 | Activity / audit log | Activity Log (Administrator); version history on each document | A-NT | |
| — | POS | — (hidden on purpose) | — | KodeERP is not the POS. POS Invoice and Point of Sale have no menu entry. POS sales come in as Sales Invoices or daily journals (template above) |
