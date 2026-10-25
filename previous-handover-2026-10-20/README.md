# KodeERP handover package

Read HANDOVER-GUIDE.pdf first. Nothing in this package has been deployed anywhere, and no DNS was changed.

- app/kodenova_theme.bundle — full git history of the KodeERP theme app (`git clone kodenova_theme.bundle kodenova_theme`)
- app/kodenova_theme-665ec44.tar.gz — the same app, clean source snapshot (no git history)
- backups/fnb.localhost/ — F&B demo (Najd Bites Food Co.): database + public files + private files
- backups/kodeerp.localhost/ — main KodeERP demo: database + public files + private files
- deploy-kit/ — Containerfile (image build), compose.yaml, compose.https.yaml (Traefik + Let's Encrypt), example.env, restore-site.sh, apps/kodenova_theme (build context)
- VERSIONS.md — exact versions
- SHA256SUMS — checksums of every file (`sha256sum -c SHA256SUMS`)

The backups contain only synthetic demo data (fictional companies, customers, suppliers and users).
They contain no site_config.json, no database passwords and no encryption key.
Demo user passwords are NOT in this package; they are hashed inside the database. Change them all after restoring (see guide).
- deploy-kit/fnb-branch-cost-centers.json — Branch -> Cost Centre mapping for fnb (site_config; see VERSIONS.md for the restore command)
