# KodeERP F&B demo tenant: setup summary

**This is a demo.** "Najd Bites Food Co." / "شركة لقمة نجد للأغذية" is a **fictional** company, and all of its data is synthetic. The VAT number **310123456700003** and the CR number **1010999999** are fake: they follow the Saudi format and are labelled "demo" on the documents. Built 20 Oct 2026 on the dev box only.

| Item | Value |
|---|---|
| Site (tenant) | `fnb.localhost`. It has its own database and is separate from the main demo (`kodeerp.localhost`, which was not changed) |
| Apps | Same as the main demo: the KodeERP core modules, HR & Payroll, and the KodeERP theme. The branding was applied automatically by the theme's install step, so no code was changed |
| Preview link | Shown in `preview/fnb-url.txt`. To start or stop it: `scripts/preview-fnb-start.sh` / `preview-fnb-stop.sh` (its own nginx on :8093 and its own quick tunnel; the main demo is not touched) |
| Company | Najd Bites Food Co., abbreviation NJB. Country Saudi Arabia, currency SAR, time zone Asia/Riyadh |
| Fiscal year | 2026, from 1 Jan to 31 Dec (**assumption**) |
| Languages | English and Arabic (right-to-left). Accounts, branches, warehouses, items, payment modes and taxes have bilingual "English \| عربي" names |
| Sign-up | Off. Login lockout after 5 failed attempts |
| Logins | Accounts Manager (EN), Accounts Manager (AR), and an Olaya Branch Manager who is limited to the Olaya branch, cost centre, warehouse and POS. Passwords are only in `.secrets/fnb_demo.txt` |

## Accounting structure (138 accounts, built on the standard chart)
- **Revenue:** an F&B Sales group with Dine-in, Takeaway, Delivery (own fleet) and Catering accounts, plus an Aggregator Sales group with HungerStation, Jahez, The Chefz and Keeta. A Sales Deductions group holds Discounts and Complimentary meals.
- **Cost of sales:** Food, Beverage and Packaging cost, Wastage & spoilage, and Staff meals.
- **Inventory:** separate accounts for raw materials (food), beverages, packaging and branch kitchens. Each warehouse is linked to its own inventory account.
- **Cash and banks:** Cash on hand, Petty cash, Bank (demo current account), Card & mada clearing, Foodics POS clearing, and Aggregator receivable clearing (the aggregator customers post here, so AR ageing shows them).
- **Expenses:** Rent, Utilities (electricity, water, gas), Salaries & staff costs (basic, housing, transport, GOSI employer share, end-of-service, iqama & work permits, medical insurance), Delivery commissions, Aggregator commissions, Bank & card/mada fees, Marketing, Repairs & maintenance, Licences & permits, and Municipality (Balady) fees.
- **Liabilities:** VAT output, Salaries payable, GOSI payable, and the end-of-service (EOSB) provision.
- **VAT 15%:**
  - Output and input VAT accounts.
  - Sales templates: VAT 15% inclusive (the default for menu prices), VAT 15% exclusive (B2B and catering), zero-rated and exempt.
  - Purchase templates: VAT 15%, zero-rated and exempt.
  - Item tax templates for the same three rates.
- **Branches:** Head Office plus Olaya (Riyadh), Malqa (Riyadh) and Tahlia (Jeddah).
  - Each has its own cost centre, a value in the "Branch" accounting dimension, its own kitchen warehouse and its own POS profile.
  - The Central Store warehouse holds three sub-stores: Food, Beverage and Packaging.
- **Payment modes:** Cash, mada, Card, Bank Transfer, Aggregator and Foodics POS, each linked to its account.
- **Item groups:** Raw Materials, Beverages, Packaging and Menu Items, each with its own default warehouse and accounts.
- **Units of measure:** Kg, g, L, ml, Pcs and Box, with conversions Kg↔g and L↔ml.
- **Print and reports:** a bilingual letterhead with the Kodenova logo as a placeholder, plus a **"KSA VAT Return (Demo)"** report. That report is a configuration record (a saved database query), not app code.

## Synthetic data (31 Aug to 19 Oct 2026)
- **Master data:** 37 stock items, 20 menu items, 8 suppliers and 10 customers. The customers are walk-in, the 4 aggregators and 5 corporate/catering clients.
- **Sales:** 212 submitted invoices.
  - Daily Foodics-style summary invoices for Olaya and Malqa, paid into Foodics clearing.
  - Daily POS invoices for Tahlia, paid by mada, card and cash.
  - Weekly aggregator invoices, and 6 catering invoices.
- **Purchases and stock:** 13 purchase invoices with stock receipt, 15 payments, and 45 stock entries (weekly transfers to the kitchens and weekly consumption, wastage and staff meals).
- **Journal entries (78):**
  - Foodics settlement (clearing split into cash and card), card/mada settlement net of fees, and cash deposits.
  - Aggregator settlements net of commission plus VAT on the commission.
  - Rent, utilities, payroll, GOSI, Balady fees, marketing and maintenance.
- **Results:** branch net profit is about SAR 187k for Olaya, 129k for Malqa and 165k for Tahlia, with Head Office costs of 90k. Stock value matches the general ledger (SAR 132k).

## Open questions for the client
1. Legal name in English and Arabic, VAT number, CR number, and the national address.
2. Branch list: names, cities, and whether each has a kitchen or a central kitchen.
3. Fiscal year: calendar year or another?
4. Opening balances and the go-live date. We will need a trial balance, stock count, open AR and AP, and fixed assets.
5. Banks and IBANs, and the card acquirer for mada (settlement timing and fee rates).
6. **Foodics: yes or no.** If yes: the daily summary or per-order detail, the payment-method mapping, and which branches use it.
7. Which aggregators they use (HungerStation, Jahez, The Chefz, Keeta, others), the commission rates and settlement cycles.
8. Menu, recipes and BOMs (for theoretical food cost), and the main suppliers.
9. Payroll in KodeERP? The number of staff, and how GOSI and WPS are handled.
10. ZATCA Phase 2 e-invoicing: their current status and their wave.

## Known limits
- Some core screens still have a few untranslated English labels in Arabic, for example a help text on the invoice form.
- The quick-tunnel URL changes whenever the tunnel restarts.
- ZATCA e-invoicing integration is **not** installed on this tenant.
