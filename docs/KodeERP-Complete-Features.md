# KodeERP complete product guide

*Every module and feature in KodeERP by Kodenova: platform, business modules, add-on services, onboarding and pricing. Status checked on the demo system on 20 Oct 2026.*

## How to read this guide

- **Included.** The feature is part of KodeERP and installed on the demo system.
- **Set up in the demo.** The feature is configured and has sample data you can try now.
- **Available, configured per client.** The feature is installed but needs client-specific setup during onboarding.
- **Service.** Kodenova delivers it as a project or add-on. It is not a built-in feature of the demo.

All data in the demo is synthetic. KodeERP is a product of Kodenova: 7+ years of business software work for clients in 13 countries.

## 1. Platform

### 1.1 Multi-tenant hosting
- Each client (tenant) gets its **own site, its own database and its own database user** on a shared server.
- Data is fully separated, and each tenant has its own users, settings, backups and upgrades.
- Each tenant can be backed up, restored or moved on its own.
- **Demo status:** the server runs 4 sites with separate databases: 1 client-facing demo site and 3 internal test sites.
- Public sign-up is off, and there is no automatic sign-up → new tenant flow yet. Kodenova creates each client site during onboarding.

### 1.2 Multi-company
- Many companies in one tenant, each with its own currency, chart of accounts, taxes, fiscal settings, warehouses and letterhead.
- Reports can run per company. Inter-company invoicing is available.
- **Set up in the demo:** 6 synthetic companies in Ecuador and Panama (USD), Saudi Arabia (SAR) and Pakistan (PKR).

### 1.3 Multi-branch
- Branch records, a cost centre per branch, a warehouse per branch, and a "Branch" accounting dimension for a branch-wise P&L.
- User permissions keep staff limited to their own branch.
- **Set up in the demo:** branch warehouses for the Ecuador company (Quito, Guayaquil) and the Saudi company (Riyadh, Jeddah).
- Branch records, branch cost centres and dimensions are available, configured per client.

### 1.4 Languages
- The full interface is in **English, Spanish and Arabic**. Arabic uses a complete right-to-left layout.
- Each user picks their own language. Printed documents follow the chosen language.
- **Set up in the demo:** all three languages, with one demo login per language.

### 1.5 Roles and permissions
- Role-based access by document type: read, write, create, submit, cancel, amend, print, email, export and report.
- Field-level permission levels, plus "only if creator" rules.
- **User permissions** restrict records by company, branch, warehouse, customer and so on.
- **Role profiles** bundle roles for quick user setup.
- **Set up in the demo:** 52 active roles and 6 role profiles. Demo users are limited to their own company.

### 1.6 Workflows and approvals
- Visual workflows with states, transitions, the role allowed at each step and conditions (for example "amount above 5,000 needs manager approval").
- Approvals work from the document or from email. Separate authorisation rules can limit approvals by amount.
- **Available, configured per client.** No workflows are set up in the demo.

### 1.7 Audit trail
- Each document keeps its version history: who changed which field, from what, to what, and when.
- Submitted accounting and stock documents cannot be edited. They must be cancelled and amended, which leaves a full trail.
- Activity and comment timelines on every record. Login activity is logged, and an access log is available.

### 1.8 Print formats and letterheads
- Branded print formats for invoices, quotations, orders and delivery notes, with letterheads per company.
- Print formats are built with a drag-and-drop builder or with custom HTML.
- Documents can be sent as PDFs by email.
- **Set up in the demo:** KodeERP-branded invoice print and 3 letterheads.

### 1.9 Email and notifications
- Send any document by email from the record, with replies threaded onto the record timeline.
- Email accounts can be used for both incoming and outgoing mail.
- Notification rules fire on events, dates or value changes, and send by email or as in-app alerts.
- Also: in-app notifications, @mentions, assignments, reminders and an auto-repeat for recurring documents.
- **Set up in the demo:** 1 email account and 8 notification rules, all with KodeERP-branded email templates.

### 1.10 Dashboards and KPI cards
- Workspaces with number cards, charts and shortcuts for each department.
- **KodeERP list KPI cards:** a Kodenova addition that shows live summary cards at the top of list pages.
- **Set up in the demo:** the KodeERP Home dashboard, 15 dashboards and 108 number cards.

### 1.11 Reports and report builder
- Hundreds of standard reports across all modules, with filters, grouping, charts and drill-down.
- The **report builder** turns any list into a custom report with chosen columns, filters, group-by and totals, which can be saved and shared.
- Query and script reports are available for advanced needs. Reports can be scheduled and emailed automatically.

### 1.12 Data import and export
- The Data Import tool loads data from CSV or Excel: insert or update, with a template download, a preview and a per-row error log.
- Any list or report can be exported to Excel or CSV.
- Used during onboarding for opening balances, customers, suppliers, items and employees.

### 1.13 REST API and integrations
- A full REST API for every document type (create, read, update, delete and query), with token or OAuth authentication.
- Webhooks push events to other systems.
- Built-in connectors include Google services, LDAP and social login (OAuth). They are configured per client.
- **Available, configured per client.** No API users or webhooks are active in the demo.

### 1.14 Mobile and responsive
- The whole system works in a mobile browser. The KodeERP theme is tested at desktop and phone widths.
- No separate app store app is needed.

### 1.15 Security
- **Password policy:** on in the demo, with a strength score and lockout after repeated failed logins.
- **Two-factor authentication** by authenticator app, SMS or email: available, off in the demo, and enabled per client.
- Session expiry, IP restrictions per user, and user permissions.
- **Backups:** database and file backups for each tenant, run on demand or on a schedule. The schedule and off-site storage are set up when a client is hosted.

## 2. Business modules

These are the modules installed on the KodeERP demo site. Our theme hides none of them: every module workspace is visible. The theme only removes vendor help links, vendor onboarding videos and setup-tour widgets.

### 2.1 Accounting
- **Chart of accounts** per company: start from a country template where one is available, from the standard chart, or import the client's own chart. Account trees support groups and sub-ledgers.
- **General ledger:** every transaction posts double-entry ledger lines and can be traced from report to voucher. The demo has more than 1,000 ledger postings.
- **Journal entries:** general, opening, depreciation, write-off and contra entries. Recurring entries are available through auto-repeat.
- **Sales invoices:** items, taxes, discounts, payment terms and due dates, credit notes and returns, and receipt of advance payments. The demo has 170.
- **Purchase invoices:** supplier bills, debit notes, landed costs and tax withholding. The demo has 28.
- **Payments:** receive, pay and internal transfer, with allocation against several invoices, partial payments and deductions. The demo has 103.
- **Payment requests and payment terms**, plus dunning letters for overdue invoices.
- **Bank accounts and bank reconciliation:** import bank statements, auto-match transactions to payments and invoices, and use reconciliation rules. Available, configured per client.
- **Taxes:** sales and purchase tax templates, item-level tax rates, tax categories and tax rules by customer or region. The demo has templates for Ecuador IVA 15%, Saudi VAT 15%, Panama and Pakistan.
- **Withholding tax** with thresholds, applied automatically.
- **Multi-currency:** transact in any currency, with exchange-rate tables, realised gain and loss postings, and **exchange-rate revaluation** of open balances. The demo has 11 currencies enabled, with invoices in USD, SAR and PKR.
- **Cost centres and budgets:** a tree of cost centres, budgets by account and period, and stop or warn rules plus budget-versus-actual reports. Available, configured per client.
- **Accounting dimensions:** add your own analysis dimensions (branch, project, department) to transactions. Available, configured per client.
- **Fiscal years and period closing:** fiscal years, accounting periods that lock closed months, and a period-closing voucher for the year end. The demo uses July–June years (2025-26 and 2026-27).
- **Inter-company transactions:** invoices and journal entries between companies in one tenant, with the mirror document created on the other side. Available, configured per client.
- **Deferred revenue and expense:** spread income and cost over a service period.
- **Subscriptions:** recurring billing plans for customers.
- **Shareholders and share transfers:** basic share register.
- **Financial reports:** Profit & Loss, Balance Sheet, Cash Flow, Trial Balance, General Ledger, Accounts Receivable and Payable (with ageing), gross profit, and sales and purchase registers. The main reports filter by company, cost centre and dimension, and a consolidated statement covers several companies.

### 2.2 Selling and CRM
- **CRM:** leads, opportunities, prospects, campaigns, sales stages, follow-up appointments and a contacts and address book.
- **Selling:** quotations, sales orders, delivery against orders, customer groups and territories, and sales partners with commissions.
- **Pricing:** price lists in several currencies, pricing rules (volume, customer, date), promotional schemes and coupon codes.
- Order-to-cash tracking: what is still to deliver and what is still to bill on each order.
- Sales analytics: sales funnel, trends and customer-wise reports.
- **Set up in the demo:** 28 customers, 6 quotations, 7 sales orders and 6 deliveries. CRM pipeline data is not loaded yet.

### 2.3 Buying
- Material requests, requests for quotation, supplier quotations and comparison, purchase orders and purchase receipts.
- Supplier groups and supplier scorecards.
- Purchase price lists, blanket orders and order-to-bill tracking.
- **Set up in the demo:** 13 suppliers and 28 purchase invoices. Purchase orders are available, configured per client.

### 2.4 Stock and inventory
- **Multi-warehouse:** a warehouse tree per company, stock transfers, goods in transit and stock per location.
- **Batches** with expiry dates, and **serial numbers** with full history from receipt to sale.
- **Valuation:** FIFO (the demo default), moving average or LIFO, with a perpetual inventory link to accounts.
- Stock entries (receipt, issue, transfer, repack), stock reconciliation, reorder levels and automatic material requests.
- Item variants (size or colour), units of measure with conversions, barcodes, item groups, quality inspection on receipt or delivery, packing slips, pick lists, shipments and delivery trips.
- Reports: stock balance, stock ledger, ageing, projected quantity and valuation.
- **Set up in the demo:** 36 items, 26 stock entries and branch warehouses. Batches and serials are available, configured per client.

### 2.5 Manufacturing
- Bills of materials with multiple levels, operations, workstations and routings.
- Production planning, work orders, job cards, material transfer for manufacture, and scrap and by-products.
- Capacity planning and production reports.
- **Subcontracting:** send raw materials to a subcontractor and receive finished goods.
- **Available, configured per client.** No bills of materials are in the demo.

### 2.6 Projects
- Projects, tasks and dependencies, a Gantt view, milestones, timesheets and activity costing.
- Project-wise billing from timesheets, plus profitability and expense tracking.
- **Available, configured per client.**

### 2.7 Assets
- Asset register, categories, depreciation schedules (straight-line, declining balance, manual), movements, maintenance, repairs, value adjustments, and asset sale or scrap with automatic accounting.
- **Available, configured per client.**

### 2.8 Quality
- Quality goals, procedures, inspections and inspection templates, reviews, feedback, actions and non-conformance records.
- **Available, configured per client.**

### 2.9 Support and helpdesk
- Issues and tickets with priority, type and service level agreements (response and resolution times).
- Warranty claims, maintenance schedules and visits (Maintenance module), and email-to-ticket.
- **Available, configured per client.**

### 2.10 Point of Sale (POS)
- Browser-based POS with POS profiles per store, item search and barcode scanning, several payment modes, receipts, and an opening and closing shift with cash reconciliation.
- Loyalty programs, and POS invoices consolidated into the accounts.
- **Available, configured per client.** No POS profile is in the demo.

### 2.11 HR
- Employees and the organisation structure (company, branch, department, designation, grade).
- **Recruitment:** job openings, applicants, interviews and offers.
- **Onboarding, transfers, promotions and separation** (employee lifecycle), with tenure tracking.
- **Leaves:** leave types and policies, allocations, applications, a holiday list and encashment.
- **Shift and attendance:** shift types, check-ins and auto-attendance.
- **Expenses:** expense claims, employee advances and travel requests.
- **Performance:** appraisals, goals, KRAs and feedback.
- Employee self-service through each employee's own login.
- **Available, configured per client.** No employees are in the demo.

### 2.12 Payroll
- Salary components, salary structures and assignments, payroll runs per period, salary slips sent by email, and accounting entries.
- **Tax and benefits:** income tax slabs, exemptions and declarations, benefit claims, gratuity, retention bonuses and incentives.
- Country-specific payroll rules are configured per client.
- **Available, configured per client.**

### 2.13 Website and customer portal
- Web pages and web forms (public or for logged-in users) built without code.
- **Customer and supplier portal:** customers see their orders, invoices, quotations and issues. Suppliers respond to requests for quotation.
- **Available, configured per client.** No web pages are published in the demo.

### 2.14 Other installed tools
- **Automation:** auto-repeat, assignment rules and scheduled reports and emails.
- **Customisation without code:** custom fields, form layouts and client or server scripts.
- **Bulk actions:** bulk transactions and bulk edit from lists.
- **Communication and telephony:** call logs, plus the email inbox linked to records.
- **Regional and EDI settings:** country-specific settings and electronic data exchange codes.

## 3. Kodenova add-ons and services

These are **services delivered by Kodenova**, not built-in features of the demo.

### 3.1 E-invoicing integrations
- Kodenova runs live client integrations with:
  - **Ecuador SRI**
  - **Guatemala FEL**
  - **El Salvador DTE**
  - **Saudi Arabia ZATCA**
- **UAE** e-invoicing: in progress.
- **Pakistan FBR:** not available.
- Connecting a client's KodeERP to its tax authority is set up per client during onboarding.
- Saudi integration is currently being tested on separate sandbox sites.

### 3.2 Custom development
- Custom documents, fields, reports, print formats, workflows and country localisation, built as KodeERP add-ons so upgrades stay clean.

### 3.3 Integrations
- Connections to e-commerce, payment, banking, shipping, BI and other business systems through the REST API and webhooks.

### 3.4 WhatsApp AI agent
- A service that connects KodeERP to WhatsApp so clients can check orders and invoices, and staff can get answers. Scoped and built per client.

### 3.5 AI connector
- A service that connects AI assistants to KodeERP data and actions with role-based limits. Scoped and built per client.

## 4. Implementation, support and pricing

### 4.1 Implementation and onboarding
All onboarding runs asynchronously by email, with no meetings required.

1. **Scope:** the client replies to a short questionnaire covering companies, branches, taxes, modules and users.
2. **Tenant:** Kodenova creates the client's own site and admin user.
3. **Companies:** country, currency, fiscal year, chart of accounts, default accounts, letterhead and logo.
4. **Taxes and e-invoicing:** tax templates, and the tax-authority connection where needed.
5. **Structure:** branches, warehouses, cost centres, the Branch dimension, users, roles and permissions.
6. **Data:** opening balances, customers, suppliers, items and employees, imported from templates.
7. **Test and go live:** an end-to-end test invoice, a short recorded walkthrough, then go-live.

### 4.2 Support
- Support by email and WhatsApp text, with updates and backups handled by Kodenova for hosted clients.
- Change requests and new features are quoted as services.

### 4.3 Pricing (proposed)
KodeERP is billed as a **subscription per tenant**, priced per user:

| Plan | Price (proposed) |
|---|---|
| Starter | $12 per user / month |
| Growth | $19 per user / month |
| Pro | $29 per user / month |

- Minimum 3 users. All prices are proposed, not final.
- Onboarding, e-invoicing integrations, custom development and AI services are quoted separately.

**Next step:** reply to this email to get your own KodeERP site.
