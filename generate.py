#!/usr/bin/env python3
"""Generate a public RSS 2.0 feed from official/vendor RSS and monitored pages.
Pages are monitored by content hash; on changes a link-only alert is emitted.
"""
import calendar
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, urlunsplit

import feedparser
import requests
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
NOW = dt.datetime.now(dt.timezone.utc)
HEADERS = {'User-Agent': 'CyberInfrastructureFeed/1.0 (+public GitHub Pages RSS aggregator)'}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def read_json(name, default):
    try:
        with open(os.path.join(BASE, name), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(name, data):
    path = os.path.join(BASE, name)
    fd, tmp = tempfile.mkstemp(dir=BASE)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def date_of(entry):
    for attr in ('published_parsed', 'updated_parsed'):
        value = entry.get(attr)
        if value:
            try:
                return dt.datetime.fromtimestamp(calendar.timegm(value), dt.timezone.utc)
            except (ValueError, OverflowError):
                pass
    return NOW


def clean_url(url):
    try:
        p = urlsplit(url)
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/') or '/', '', ''))
    except ValueError:
        return url


def key_of(title, url):
    cves = sorted(set(re.findall(r'CVE-\d{4}-\d{4,}', title, flags=re.I)))
    if cves:
        return 'cve:' + ','.join(x.upper() for x in cves)
    return 'url:' + clean_url(url)


def main():
    config = read_json('sources.json', {'feeds': [], 'pages': []})
    state = read_json('state.json', {'items': {}, 'pages': {}})
    old_items = state.get('items', {})
    old_pages = state.get('pages', {})
    items = dict(old_items)
    failures = []
    results = []
    successful = 0

    for source in config['feeds']:
        try:
            r = SESSION.get(source['url'], timeout=18)
            r.raise_for_status()
            parsed = feedparser.parse(r.content)
            if not parsed.entries:
                raise ValueError('No RSS/Atom entries returned')
            successful += 1
            results.append({'source':source['name'],'mode':'rss','status':'ok','entries_available':len(parsed.entries)})
            for e in parsed.entries[:60]:
                title = BeautifulSoup(e.get('title', ''), 'html.parser').get_text(' ', strip=True)[:240]
                url = e.get('link', '')
                if not title or not url.startswith('https://'):
                    continue
                published = date_of(e)
                if published > NOW + dt.timedelta(days=1):
                    published = NOW
                if published < NOW - dt.timedelta(days=120):
                    continue
                key = key_of(title, url)
                item = {'title': title, 'url': url, 'source': source['name'], 'category': source['category'],
                        'published': published.isoformat(), 'description': BeautifulSoup(e.get('summary', ''), 'html.parser').get_text(' ', strip=True)[:700]}
                existing = items.get(key)
                if existing is None or (source['category'] != 'News' and existing.get('category') == 'News'):
                    items[key] = item
        except Exception as exc:
            failures.append(f"{source['name']}: {str(exc)[:160]}")
            results.append({'source':source['name'],'mode':'rss','status':'failed','error':str(exc)[:160]})

    for source in config['pages']:
        try:
            r = SESSION.get(source['url'], timeout=18)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            main_content = soup.find('main') or soup.find('article') or soup.body or soup
            content = re.sub(r'\s+', ' ', main_content.get_text(' ', strip=True))[:100000]
            if len(content) < 100:
                raise ValueError('Page content unavailable or too short')
            digest = hashlib.sha256(content.encode()).hexdigest()
            previous = old_pages.get(source['url'])
            if previous and previous != digest:
                key = 'page:' + hashlib.sha256((source['url'] + digest).encode()).hexdigest()[:24]
                items[key] = {'title': source['name'] + ' — official page changed (review required)',
                              'url': source['url'], 'source': source['name'], 'category': source['category'],
                              'published': NOW.isoformat(),
                              'description': 'A monitored official page changed. This is a change notification, not a verified new security advisory.'}
            old_pages[source['url']] = digest
            successful += 1
            results.append({'source':source['name'],'mode':'page-change','status':'ok','changed':bool(previous and previous != digest)})
        except Exception as exc:
            failures.append(f"{source['name']}: {str(exc)[:160]}")
            results.append({'source':source['name'],'mode':'page-change','status':'failed','error':str(exc)[:160]})

    if successful == 0 and not items:
        raise RuntimeError('No sources available; refusing to publish an empty feed')
    cutoff = NOW - dt.timedelta(days=60)
    items = {k: v for k, v in items.items() if dt.datetime.fromisoformat(v['published']) >= cutoff}
    ordered = sorted(items.values(), key=lambda x: x['published'], reverse=True)[:300]
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    for tag, val in [('title', 'Cybersecurity & IT Infrastructure Intelligence'),
                     ('link', 'https://pbanga-au.github.io/cyber-infrastructure-feed/'),
                     ('description', 'Security, cloud, network, PKI and infrastructure advisories from official and selected news sources.'),
                     ('language', 'en'), ('lastBuildDate', email.utils.format_datetime(NOW))]:
        ET.SubElement(channel, tag).text = val
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link',
                  {'href': 'https://pbanga-au.github.io/cyber-infrastructure-feed/feed.xml', 'rel': 'self', 'type': 'application/rss+xml'})
    for i in ordered:
        node = ET.SubElement(channel, 'item')
        for tag, val in [('title', i['title']), ('link', i['url']), ('guid', i['url']),
                         ('description', f"[{i['category']}] {i['source']}: {i['description']}"),
                         ('pubDate', email.utils.format_datetime(dt.datetime.fromisoformat(i['published']))),
                         ('category', i['category'])]:
            el = ET.SubElement(node, tag)
            if tag == 'guid':
                el.set('isPermaLink', 'false')
            el.text = val
    ET.indent(rss)
    ET.ElementTree(rss).write(os.path.join(BASE, 'feed.xml'), encoding='utf-8', xml_declaration=True)
    save_json('state.json', {'items': items, 'pages': old_pages})
    with open(os.path.join(BASE, 'status.json'), 'w', encoding='utf-8') as f:
        json.dump({'last_run_utc': NOW.isoformat(), 'sources_successful': successful, 'failures': failures, 'items_published': len(ordered), 'source_results': results}, f, indent=2)
    print(f'Published {len(ordered)} items; {successful} sources succeeded; {len(failures)} failed')
    for failure in failures:
        print('WARNING:', failure)


if __name__ == '__main__':
    main()
