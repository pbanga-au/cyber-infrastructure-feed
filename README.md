# Cybersecurity & IT Infrastructure Intelligence Feed — v3

Public URL: https://pbanga-au.github.io/cyber-infrastructure-feed/feed.xml

## Deployment
Upload the files to the repository root, preserving `.github/workflows/update.yml`.
The workflow runs hourly or manually and commits `feed.xml`, `state.json`, and `status.json`.
Keep the existing `state.json` if present to preserve prior articles and page-monitor baselines.

## Diagnostics
`status.json` lists each source with `ok` or `failed`. A page monitor reporting `ok` means the page was readable, **not** that individual security advisories were extracted. `feed.xml` may still contain articles from previous successful runs.

## Limitations
Some vendor pages use JavaScript, bot controls or authentication; this generator cannot guarantee complete vendor coverage. Page changes generate review notifications, not verified advisories. Feed links and endpoints have not all been live-tested in this package. The invalid Google Cloud RSS endpoint and unreachable Megaport status domain were removed; Google Cloud and Megaport official page monitors remain configured. AWS status RSS was added but is not yet live-verified. Cross-publication CVE deduplication can merge distinct articles about the same CVE.
