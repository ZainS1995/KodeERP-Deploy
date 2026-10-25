# ZATCA Phase 2 on ERPNext v16: go/no-go test

Date: 2026-10-19 (Asia/Karachi). Environment: KodeERP box sandbox (see `SETUP.md`). Data: synthetic only.
No taxpayer data, no ZATCA account signup, no Fatoora portal login. The only ZATCA endpoint tried was the public
developer-portal sandbox, with ZATCA's published sandbox OTP `123345`.

## Verdict (short)

| | zatca_erpgulf (ERPGulf) | ksa_compliance (Lavaloon) |
|---|---|---|
| Installs on Frappe 16.52.0 / ERPNext 16.51.1 | **Yes**, clean | **Yes**, clean |
| `bench migrate` | **Yes**, clean | **Yes**, clean |
| CSR generation | **Yes** | **Yes** (via bundled ZATCA SDK CLI) |
| Sandbox onboarding (compliance CSID, OTP 123345) | **Not verified**: box can't reach ZATCA (see blocker) | **Not verified**: same blocker |
| Phase 2 simplified invoice: UBL XML + signature + QR | **Yes, offline**. ZATCA SDK: XSD/EN/KSA/QR/SIGNATURE/PIH **PASSED** | **Yes, offline**. ZATCA SDK: XSD/EN/KSA/QR/SIGNATURE/PIH **PASSED** |
| Phase 2 standard invoice: UBL XML | **Yes, offline**. XSD/EN/KSA/PIH **PASSED** | **Yes, offline**. XSD/EN/KSA/PIH **PASSED** |
| Hash chain (PIH/ICV) | Uses a fixed starting PIH; only moves to the next PIH after ZATCA **accepts** an invoice, so chaining couldn't be shown offline | **Chains at generation**: invoice 2 PIH = invoice 1 hash (shown) |
| Reporting (simplified) / clearance (standard) | **Not verified** (blocker) | **Not verified** (blocker) |
| Licence | MIT | **AGPL-3.0** (see licensing note) |

**Overall: conditional GO.** Both apps install, migrate, and produce invoices on v16 that pass ZATCA's own SDK
validation offline: UBL 2.1 XML, XAdES signature, TLV QR (tags 1–9 on simplified) and PIH. **The live ZATCA API
step (CSID onboarding, reporting, clearance) is untested** because this box can't open a TLS connection to ZATCA's
gateway. So the verdict per app is:

- **ksa_compliance: works (offline-verified), with configuration fixes listed below.** The API leg still needs a networked test.
- **zatca_erpgulf: works (offline-verified), with configuration fixes listed below.** The API leg still needs a networked test.
  - Its starting PIH is a fixed value rather than ZATCA's documented initial hash. Confirm that the sandbox accepts it.

Neither app has "doesn't work" evidence. Clearing that last step needs about 30 minutes on any machine that can reach
`gw-fatoora.zatca.gov.sa`. The scripted steps are below.

> **Update 2026-10-19 ~22:30 PKT (UTC+5):** the box was reset after an out-of-memory full `bench build`. The MariaDB volume was lost, including both ZATCA test sites (`zatca-erpgulf.localhost`, `zatca-ksa.localhost`). The evidence files under `verify/zatca/` (signed XML, QR, validator output) survived and still support the verdict. The app checkouts (`apps/zatca_erpgulf`, `apps/ksa_compliance`) are intact and rebuilt. Re-running the egress check from the box still fails (`curl` to gw-fatoora.zatca.gov.sa returns 000, TLS/connection failure), so the live-sandbox leg remains blocked. To re-test, recreate the sites with `scripts/new-site.sh` and follow the scripted re-test below.

## Blocker (exact)

- From the box (and from containers on host networking), every HTTPS connection to `gw-fatoora.zatca.gov.sa`,
  `fatoora.zatca.gov.sa` and `sandbox.zatca.gov.sa` fails during the TLS handshake:
  `error:0A000126:SSL routines::unexpected eof while reading`. The box's egress proxy resolves these hosts to
  `198.18.0.1`. TLS 1.2, TLS 1.3 and HTTP/1.1 all fail the same way.
  Sending traffic through the explicit egress proxy returns HTTP 500.
- `zatca.gov.sa` (the main site) is reachable, and the gateway itself is up: a fetch from a different network got
  `{"code":"Invalid-Request","message":"System failed to process your request"}` from
  `.../developer-portal/compliance`. So ZATCA or the box's egress provider is blocking this box's egress path to
  the e-invoicing gateway. It isn't an app bug.
- App-level errors, which confirm both apps reach the HTTP call and fail only on the network:
  - ksa_compliance `onboard(otp=123345)` → `requests.exceptions.SSLError: HTTPSConnectionPool(host='gw-fatoora.zatca.gov.sa', port=443): Max retries exceeded with url: /e-invoicing/developer-portal/compliance (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] ...')))`
  - zatca_erpgulf `create_csid` → the same SSLError on `/e-invoicing/developer-portal/compliance`.
- **What's needed:** run the scripted test from a network with normal egress to `gw-fatoora.zatca.gov.sa:443`
  (a laptop, a small cloud VM, or a staging server), or get the box's egress allow-listed for that host.
  I didn't try VPNs or other ways around the block.

## Versions tested

| Component | Version / commit |
|---|---|
| Frappe | 16.52.0 (version-16 @ 4515014) |
| ERPNext | 16.51.1 (version-16 @ 5af6561) |
| zatca_erpgulf | 3.0.1, branch `main` @ `3f69ce03438537e0e13e0c86747d57af7e2e9bf8` (2026-10-16, "Merge PR #277 … Version 16 fix"). `pyproject` declares `frappe >=14,<17`. |
| zatca_erpgulf `zatca16` branch | **not used**: stale (last commit 2026-01-26 @ 72a0dc9d, 31 commits *behind* `main`; `main` is 197 ahead and has the v16 fix merged). Use `main`. |
| ksa_compliance | 0.61.11, branch `master` @ `91250282f4fe936e015bb0208041f29ae3c54a39` (2026-10-08). Declares `frappe >=15,<17`. |
| ZATCA CLI (installed by ksa_compliance) | lavaloon-eg/zatca-cli 2.10.0, which bundles the **official ZATCA SDK jar `zatca-einvoicing-sdk-238-R3.4.5`** plus Temurin JRE 11.0.23 |

Test sites (one per app, so their Sales Invoice hooks don't clash; the main site `kodeerp.localhost` is untouched):
`zatca-erpgulf.localhost` and `zatca-ksa.localhost`. Each has ERPNext plus that one app, and the company
"Synthetic Saudi Trading Co" (SST): Saudi Arabia, SAR, Asia/Riyadh, VAT `399999999900003` (ZATCA's documented test VAT).
The buyers are a B2C walk-in and a B2B buyer with VAT `300000000000003`. One item, 2 × 100 SAR plus 15% VAT, so 230.00 SAR.

## Test steps and evidence

### Install and migrate
```
bench get-app --branch main https://github.com/ERPGulf/zatca_erpgulf          # OK
bench get-app --branch master https://github.com/lavaloon-eg/ksa_compliance     # OK
scripts/new-site.sh zatca-erpgulf.localhost && bench --site zatca-erpgulf.localhost install-app zatca_erpgulf && bench --site … migrate   # exit 0/0/0
scripts/new-site.sh zatca-ksa.localhost     && bench --site zatca-ksa.localhost install-app ksa_compliance && bench --site … migrate      # exit 0/0/0
```
There were no errors or deprecation warnings in the install or migrate logs (`/workspace/kodeerp/zatca-site{1,2}.log`).
`ModuleNotFoundError` entries in the worker log date from *before* the bench restart: the old worker hadn't imported the
newly fetched apps yet. This is an ops note: restart workers after `get-app`. It isn't an app defect.

### ksa_compliance (offline Phase 2)
1. `ksa_compliance.zatca_cli.setup` downloaded the JRE and ZATCA CLI → `check_setup` → "Version 2.10.0".
2. ZATCA Business Settings created (Sandbox server, Live sync, automatic VAT 15% account, XML validation on).
3. `onboard(otp="123345")`: CSR generated (`zatca-files/<settings>.csr`), then the API call failed (blocker).
4. For an **offline-only** test I wrote a **self-signed** X.509 cert for the app's built-in sandbox key, named so
   the app picks it up (`zatca-files/<settings>.pem` / `-compliance.pem`).
   `CN=KODEERP-SELF-SIGNED-OFFLINE-TEST-…`. It isn't a ZATCA-issued certificate and is never sent anywhere.
5. Submitted `ACC-SINV-2026-00001` (B2C, simplified, type `388`/`0200000`) and `ACC-SINV-2026-00002` (B2B, standard, `388`/`0100000`).
   The app generated, signed and validated each one with the ZATCA SDK:

| Invoice | ICV | SDK result | PIH | Invoice hash |
|---|---|---|---|---|
| 00001 simplified | 1 | XSD, EN, KSA, QR, SIGNATURE, PIH **PASSED** | `NWZlY2Vi…NTdlOQ==` (ZATCA's initial hash, base64 of SHA-256("0")) | `1aGLtbaVx1ByQUsCZc3Ne32Jb5+KwZ5IeIAnLq7FK74=` |
| 00002 standard | 2 | XSD, EN, KSA, PIH **PASSED** (QR/signature for standard invoices come from ZATCA at clearance) | `1aGLtbaVx1ByQUsCZc3Ne32Jb5+KwZ5IeIAnLq7FK74=` = hash of 00001 ✔ chain | `xGZHViMfeB6kY/v1j7sjUqhrsYeHEINzuMrA7mT+IOw=` |

   - Both invoices had one warning: `BR-KSA-37 seller building number must contain 4 digits`. Business Settings
     `building_number` didn't stick on the API create (Address `custom_building_number` was set afterwards).
     That's a configuration fix, not a code fix.
   - Decoded QR TLV (simplified): 1 = seller name, 2 = VAT 399999999900003, 3 = timestamp, 4 = 230.0 total,
     5 = 30.0 VAT, 6 = invoice hash, 7 = ECDSA signature, 8 = public key, 9 = certificate signature.
   - Integration status `Ready For Batch`. Sending stopped with `Password not found … production_secret`,
     which is expected with no CSID.
   - Files: `verify/zatca/ksa_compliance-{simplified,standard}-*.xml` and `verify/zatca/ksa_compliance-*-qr.png`.

### zatca_erpgulf (offline Phase 2)
1. Company set to Phase-2, Sandbox, OTP `123345`, CSR config (synthetic), CRN.
2. `sign_invoice_first.create_csr` → CSR returned (base64 PEM). `create_csid` → SSLError (blocker).
3. Offline only: a **self-signed** cert for the app's generated private key was put in `Company.custom_certificate`.
4. Submitted `ACC-SINV-2026-00001` (B2C, simplified) and `ACC-SINV-2026-00002` (B2B, standard).
   The app built and signed the XML, then stopped at `Production CSID for company SST not found` (expected).
   I validated the generated XML myself with the same official ZATCA SDK (via zatca-cli `validate`):

| Invoice | SDK result | PIH in XML |
|---|---|---|
| 00001 simplified (`0200000`) | XSD, EN, KSA, QR, SIGNATURE, PIH **PASSED**; `isValid: true, isValidQr: true, isValidSignature: true` | `6G6AZCE7wl6Ahy9mQWLu7Euo43Qmf6uHceioxUpnmx8=` (app default `custom_pih`) |
| 00002 standard (`0100000`) | XSD, EN, KSA, PIH **PASSED**; `isValid: true` | the same value. The app doesn't move to the next PIH until ZATCA accepts an invoice, so offline the chain stays put |

   - The PIH check here only shows the PIH I passed matches the XML. Real chaining needs the networked test.
   - Files: `verify/zatca/zatca_erpgulf-{simplified,standard}-*.xml` and `verify/zatca/zatca_erpgulf-simplified-qr.png`.

## Fixes / configuration needed (none required code changes)

| App | Issue | Fix |
|---|---|---|
| both | Egress to ZATCA gateway blocked from this box | Run the API leg from a networked machine or staging. Allow-list `gw-fatoora.zatca.gov.sa:443`. |
| both | Workers started before `get-app` raise `ModuleNotFoundError` | Restart bench or workers after installing apps (standard practice). |
| zatca_erpgulf | B2B invoice failed: "Customer address is mandatory for non-B2C customers" even with `customer_address` set on the invoice | On v14+ the app reads `Customer.customer_primary_address`. Set the primary address on B2B customers. |
| zatca_erpgulf | First PIH default is `6G6AZ…` rather than ZATCA's documented initial hash (base64 of SHA-256("0"), `NWZlY2Vi…`); the PIH only moves on after ZATCA accepts an invoice | Check against the sandbox in the networked run. Review the chaining behaviour for rejected or offline invoices. |
| zatca_erpgulf | No VAT account or tax template on a fresh v16 KSA company | Create the VAT 15% account and template, or use the setup page (`/desk/setup-zatca-phase-2`). |
| ksa_compliance | BR-KSA-37 warning | Set the 4-digit building number in ZATCA Business Settings and the company Address. |
| zatca_erpgulf | The repo ships `cert.pem` in its root: a simulation certificate for a third-party test company ("Maximum Speed Tech Supply LTD", TST-…-399999999900003) | Not used. Note it in a security review; it holds no private key. |

## Licensing note

- **ksa_compliance is AGPL-3.0.** If KodeERP runs it in a hosted SaaS and modifies it, we must offer the modified
  source to users who interact with it over the network. Using it unmodified, as a separate app, is lower risk, but
  AGPL still applies to the combined service.
  - ERPNext itself is GPL-3.0, so the stack is copyleft either way. AGPL adds the network-use clause.
  - This needs legal sign-off before we sell a hosted product.
- **zatca_erpgulf is MIT**: permissive, and the simpler choice for a commercial SaaS. Keep the copyright notice.
- Neither app is affiliated with ZATCA. Before claiming compliance to customers, use a ZATCA-listed solution
  provider or complete ZATCA onboarding as the taxpayer.

## Scripted networked re-test (to finish the go/no-go)

On any machine that can `curl -X POST https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal/compliance`
and get JSON back (even an error), using the same repo and commits:

1. Bring up the stack from `SETUP.md`, then `get-app` both apps at the commits above.
2. **ksa_compliance:** Business Settings (Sandbox) → `Create CSR` with OTP `123345` → `Perform compliance checks`
   (the app sends ZATCA's 6 compliance sample documents) → `Get production CSID` (OTP `123345`) → submit one B2C
   and one B2B invoice. **Pass:** integration status `Accepted` / `Accepted with warnings` (reporting, then clearance).
3. **zatca_erpgulf:** Company → Create CSR → Generate Compliance CSID → Check Compliance → Generate Production CSID
   → submit the same two invoices. **Pass:** `custom_zatca_status` `REPORTED` / `CLEARED`, and the PIH moves
   from invoice 1 to invoice 2.
4. Record the API responses in this file and update the verdict.

Remove the self-signed offline certificates before doing this. The real CSID flow overwrites them.
