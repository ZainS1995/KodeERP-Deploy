# KodeERP capabilities overview

*Multi-tenant, multi-company and multi-branch ERP by Kodenova. Status as checked on the demo system, 20 Oct 2026.*

## At a glance

| Topic | Supported by the platform | Set up in our demo today |
|---|---|---|
| Multi-tenant | Yes. Each client gets its own site and its own database on a shared server | 1 client-facing demo site. 3 internal test sites. Self-service signup is off. No automatic provisioning yet |
| Multi-company | Yes. Unlimited companies per tenant, each with its own currency and chart of accounts | 6 synthetic companies in USD, PKR and SAR |
| Multi-branch | Yes, using branches, cost centres, warehouses, accounting dimensions and user permissions | Branch warehouses for 2 companies. Branch records, branch cost centres and dimensions are not configured yet |
| Languages | English, Spanish, Arabic (right-to-left) | All three enabled, with one demo login per language |

## 1. Multi-tenant: one server, fully separate clients

- **How it works.** Every client (tenant) gets its **own site with its own database and its own database user**. Their data never shares tables with another client. Each client gets its own address, users, settings, backups and upgrades, while all of them run on one shared server. This keeps hosting costs low.
- **Isolation.** A user of one client cannot log in to another client's site. Each site can be backed up, restored, moved or deleted on its own.
- **Today.** The server runs 4 sites, each with a separate database: the KodeERP demo, one restore-test site and two Saudi e-invoicing test sites. Only the demo site is used for clients.
- **Not built yet.** Public sign-up is disabled, and there is no automatic "sign up → new tenant" flow. We create each new client site by hand with a script during onboarding, which takes minutes. Automating this is a future step.

## 2. Multi-company: several legal entities in one tenant

- One tenant can hold many companies, for example a holding company and its subsidiaries in different countries.
- Each company has its own **currency, chart of accounts, fiscal settings, taxes, warehouses, cost centres and letterhead**. Reports can be run per company.
- **Demo example (all synthetic):**

| Company | Country | Currency |
|---|---|---|
| Kodenova Demo Trading S.A. | Ecuador | USD |
| Distribuidora Andina Demo S.A. | Panama | USD |
| شركة كودنوفا للتجارة التجريبية | Saudi Arabia | SAR |
| شركة الواحة للتجارة - تجريبية | Saudi Arabia | SAR |
| Kodenova Demo Trading | Pakistan | PKR |
| KodeERP Sandbox Co | Pakistan | PKR |

- The demo users are limited to their own company. For example, the Spanish and English demo users see only the Ecuador company, and the Arabic user sees only the Saudi company.

## 3. Multi-branch: one company, many locations

KodeERP uses five building blocks for branches. Each one is a standard feature that we configure for each client:

1. **Branch** records, such as Quito, Guayaquil, Riyadh and Jeddah. They are used on employees and HR records.
2. **A cost centre per branch**, so income and expenses are posted to the right branch.
3. **A warehouse per branch**, for stock levels, transfers and deliveries by location.
4. **Accounting dimensions** (for example a "Branch" dimension) on invoices, payments and journals, which give a **branch-wise P&L** and balance sheet.
5. **User permissions**, so staff see and post only for their own branch, warehouse or company.

**In the demo today:** branch warehouses exist for the Ecuador company (Bodega Quito, Showroom Guayaquil) and the Saudi company (Riyadh showroom, Jeddah warehouse). User permissions are used at company level. Branch records, branch cost centres (each company has only "Main") and accounting dimensions are **not configured yet**. Setting these up is part of each client's onboarding.

## 4. Accounting

- **Chart of accounts per company.** Start from a country template where one is available, or from the standard chart, or import the client's own chart. Each demo company has about 95 accounts on the standard chart.
- **General ledger and journal entries** with full drill-down from reports to vouchers. The demo has more than 1,000 ledger postings.
- **Sales and purchase invoices.** The demo has 170 sales invoices and 28 purchase invoices across the companies.
- **Payments and bank reconciliation:** payment entries (103 in the demo), matching against bank statements, and outstanding tracking.
- **Taxes.** Tax templates for each company and country. The demo has Ecuador IVA 15% and Saudi VAT 15% templates, among others.
- **E-invoicing experience.** Kodenova has live tax integrations for clients with **Ecuador SRI, Guatemala FEL, El Salvador DTE and Saudi ZATCA**. **UAE** is in progress. Connecting a client's KodeERP to its tax authority is set up during onboarding. Saudi integration is being tested on separate sandbox sites. Pakistan FBR is **not** available.
- **Multi-currency.** Invoices and payments can be in any currency, with exchange rates, gain or loss postings and **exchange-rate revaluation** of open balances. The demo has 11 currencies enabled, and invoices are issued in USD, SAR and PKR.
- **Cost centres and budgets**, with budget-versus-actual control and warnings.
- **Fiscal years and period closing**, with accounting periods that lock closed months. The demo uses July–June fiscal years (2025-26 and 2026-27).
- **Financial reports:** Profit & Loss, Balance Sheet, Cash Flow, Trial Balance, General Ledger, and Accounts Receivable and Payable ageing. All of them can be filtered by company, cost centre or dimension.
- **Inter-company transactions.** Companies in one tenant can invoice each other, and the matching purchase or sales document is created on the other side. This is configured per client and is not set up in the demo.

## 5. Company setup and onboarding

**A company record holds** its name and abbreviation, country, default currency, chart of accounts, default accounts (receivable, payable, income, expense, cash, bank, rounding), fiscal year, tax IDs and address, letterhead and logo for printed documents, and its default warehouses and cost centre. All six demo companies have their default accounts set. The demo also has 3 letterheads.

**How a new client is set up (async, by email):**

1. Create the client's own site (tenant) and admin user.
2. Create the company or companies: country, currency, fiscal year and chart of accounts.
3. Set up tax templates and, where needed, the e-invoicing connection.
4. Add branches, warehouses, cost centres and the Branch dimension.
5. Import opening balances, customers, suppliers and items.
6. Create users, roles and branch permissions. Add the letterhead and logo.
7. Run a test invoice end to end, then go live.

## 6. Other modules

**Selling** (quotations, sales orders, deliveries), **Buying** (requests, purchase orders, receipts), **Stock and inventory** (warehouses, transfers, batches and serials, valuation), **CRM** (leads, opportunities), **HR and payroll**, **Projects** (tasks, timesheets), **Manufacturing** (bills of materials, work orders), **Point of Sale** and **Assets**.

The demo has sample data for selling, buying and stock: 36 items, 28 customers, 13 suppliers, quotations, sales orders, deliveries and stock entries. CRM, HR and payroll, Projects, Manufacturing and POS are installed but have no demo data yet.

**Languages:** the whole interface works in **English, Spanish and Arabic**, and Arabic uses a full right-to-left layout.

## 7. What this means for clients

- **Their data stays private:** each client has its own database.
- **They can grow inside one system,** from more branches to more companies and more countries.
- **They see branch performance** through branch-wise P&L, stock and permissions once configured.
- **It runs in their language and currency,** with their tax setup.

## 8. Pricing tie-in

KodeERP is a **subscription per tenant** (one client site), billed by the number of users:

| Plan | Price (proposed) |
|---|---|
| Starter | $12 per user / month |
| Growth | $19 per user / month |
| Pro | $29 per user / month |

Minimum 3 users. Prices are proposed, not final. Proposed: all companies and branches inside one tenant are covered by the same subscription.
