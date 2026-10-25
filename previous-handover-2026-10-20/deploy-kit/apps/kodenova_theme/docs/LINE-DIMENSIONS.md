# Line cost centre / Branch sync

**What it does.** On Sales Invoice, Purchase Invoice, POS Invoice, Sales Order, Delivery Note,
Purchase Order and Purchase Receipt (including returns / credit and debit notes), every item line
and every tax line takes the header **Cost Center** and the header value of each enabled
**accounting dimension** (e.g. Branch) when that line is:

- empty, or
- still on the company default (Company › Default Cost Center, or the dimension's company
  default) while the header has a different value.

A line deliberately set to another non-default value (e.g. one item booked to Malqa on an Olaya
invoice) is never changed. If the header itself is the company default (Head Office), lines are
left alone.

Why: ERPNext copies the header cost centre only into empty item rows and gives default tax rows
the company cost centre, so branch invoices posted income/expense and VAT on Head Office while
Branch said Olaya. With the sync, P&L by Cost Centre and P&L by Branch agree.

**Where.**
- Server (authoritative): `kodenova_theme/accounting/line_dimensions.py`, wired in `hooks.py`
  `doc_events` (`before_validate` and `validate`). It only sets values the header already carries,
  so branch managers' user permissions are unaffected.
- Desk (live): `public/js/kodeerp_line_dims.js` — changing the header Cost Centre / Branch updates
  lines that are empty, on the company default, or still on the previous header value; new item
  lines and tax-template rows follow the header.

**Toggle** (default ON):

```
bench --site <site> set-config -p kodeerp_sync_line_dimensions 0   # off (core ERPNext behaviour)
bench --site <site> set-config -p kodeerp_sync_line_dimensions 1   # on
```

**Tests.** `kodenova_theme/tests/test_line_dimensions.py` (no site needed):

```
cd frappe-bench/sites && ../env/bin/python -m unittest kodenova_theme.tests.test_line_dimensions -v
```

Plus the F&B regression (`development/qa/fnb_regress.py`, cases `r_dims`, `r_dims_mgr`, `r_mgr_pi`).

## Header Cost Centre from Branch (v0.8)

When a document's **Branch** is set or changed and its header **Cost Center** is empty or the
company default (Head Office), the header takes that branch's cost centre; the line sync above then
moves the item and tax lines. A header Cost Centre deliberately set to a different value is never
changed by the server. On the desk form it also follows when it is still on the previous branch's
cost centre (e.g. switching Olaya → Malqa moves Olaya Branch → Malqa Branch).

The mapping is site configuration, not code (`site_config.json`):

```
bench --site fnb.localhost set-config -p kodeerp_branch_cost_centers \
  '{"Najd Bites Food Co.": {"Olaya, Riyadh | العليا - الرياض": "Olaya Branch | فرع العليا - NJB", ...}}'
```

Entries whose cost centre does not exist, belongs to another company or is a group are ignored.
No mapping = no change. Toggle (default ON): `kodeerp_branch_cost_center_sync` (0 = off).
Both rules are fail-safe: on an unexpected error they write an Error Log
("KodeERP line dimension sync") and the save continues.

A site moved to a new server keeps the mapping only if `site_config.json` values are carried
over (or set again with the command above).
