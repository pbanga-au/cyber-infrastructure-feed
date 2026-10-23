# Cybersecurity & IT Infrastructure Intelligence Feed

Public RSS aggregator for `pbanga-au`.

**Planned public URL:** https://pbanga-au.github.io/cyber-infrastructure-feed/feed.xml

## Setup

1. Extract this ZIP and upload its **contents** (including the hidden `.github` folder) to the root of the public `pbanga-au/cyber-infrastructure-feed` repository. GitHub's web upload may not preserve hidden folders reliably; using `git` locally is recommended.
2. In repository **Settings > Pages**, choose **Deploy from a branch**, branch **main**, folder **/(root)**, then Save.
3. In **Actions**, run **Update public RSS feed** manually once. Future runs are scheduled hourly (GitHub may delay or skip scheduled runs).
4. Open the feed URL. Check `status.json` for failed sources.

## Important limitations

- Feed URLs in `sources.json` are **candidate endpoints**; not all have been live-tested. Unavailable feeds are reported in `status.json` and do not silently count as working.
- Pages without RSS are **change-monitored**, not parsed into individual advisories. The first successful retrieval establishes a baseline and produces no alert. Subsequent page changes generate an explicitly labelled review notice; routine page changes may cause false positives.
- CVE matching and canonical URL matching provide **basic deduplication**, not semantic event correlation. An advisory referencing multiple CVEs may merge imperfectly.
- This is not a guaranteed alerting or outage monitoring system. Use vendor security mailing lists and official status notifications for urgent response.
- Public repository state and feeds contain public source information only. Do not put secrets or internal system details in this repository.
- Scheduled jobs require repository Actions to be enabled, and GitHub Pages must be configured separately.
- Source terms and access restrictions must be respected; sources may block automated requests.

## Coverage

CISA, ACSC, UK NCSC, Palo Alto Networks, Juniper/Mist, Arista (including relevant VeloCloud advisories), HPE Aruba, ZPE, Megaport, AWS, Azure, Google Cloud, GoDaddy/Mozilla CA incidents, OpenSSL, and selected security publications. Some are page-change monitors only.

## Local test

```sh
python3 -m pip install -r requirements.txt
python3 generate.py
```
