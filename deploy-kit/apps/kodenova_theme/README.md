### Kodenova Theme

Kodenova brand theme and UX layer for KodeERP (ERPNext v16)

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app kodenova_theme
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/kodenova_theme
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit

## KodeERP branding (v0.2)

- `public/css/kodenova_theme.css`: brand tokens mapped onto Frappe v16 CSS variables; styles the sidebar, page head, cards, forms, buttons (including Espresso `es-button`), login and RTL.
- `public/css/kodenova_fonts.css` + `public/fonts/`: self-hosted Inter, Urbanist, DM Mono and Noto Sans Arabic (OFL-1.1, see `THIRD_PARTY_NOTICES.md` and `licenses/`).
- `public/images/kodenova-*`: official Kodenova logo (from kodenova.com, unchanged) plus white variant, favicon and app tiles; `kodeerp-lockup*.png` = K mark + KodeERP wordmark (with/without "by Kodenova"); legacy `kodeerp-*.svg` filenames wrap the same mark.
- `branding.py`: on `after_install` and `after_migrate`, sets the brand name, logo and favicon in Website, Navbar and System Settings (idempotent).
- `public/js/kodenova_web.js`: login brand row and the upstream attribution line.

Frappe (MIT), ERPNext (GPL-3.0) and HRMS (GPL-3.0) aren't modified, and their notices stay in place.

## Line cost centre / Branch sync (v0.7)

Item and tax lines on sales/purchase documents follow the header Cost Center and Branch (and any
other accounting dimension) when they are empty or still on the company default. Toggle with
site_config `kodeerp_sync_line_dimensions` (default on). Details: [docs/LINE-DIMENSIONS.md](docs/LINE-DIMENSIONS.md).
