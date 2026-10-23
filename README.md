# Cybersecurity & IT Infrastructure Intelligence Feed — v2

Public RSS: https://pbanga-au.github.io/cyber-infrastructure-feed/feed.xml

## Upgrade

Upload the contents of this package to the repository root, replacing existing `generate.py`, `sources.json`, `requirements.txt` and `README.md`. Update `.github/workflows/update.yml` separately using GitHub's file editor if the browser upload omits the hidden `.github` directory. Trigger the workflow manually once.

## Verify

Open `https://pbanga-au.github.io/cyber-infrastructure-feed/status.json` after the run. `source_results` lists `ok` or `failed` for every source. `mode=rss` yields individual entries; `mode=page-change` only alerts after the monitored page's content changes. First run establishes a baseline. This does NOT guarantee full vendor advisory coverage.

Some official pages may reject automated retrieval or change layout. Endpoints are candidates, not all live verified. Use vendor subscription and status channels for urgent notifications. Basic CVE/URL deduplication only. GitHub schedules may be delayed.
