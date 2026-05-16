from __future__ import annotations

import json
import re
import subprocess
import sys
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

from .models import StreamCandidate

M3U8_RE = re.compile(r'https?:\\?/\\?/[^\"\'<>\s]+?\.m3u8[^\"\'<>\s]*', re.I)


def normalize_url(raw: str) -> str:
    url = raw.replace('\\/', '/')
    return unquote(url).strip('"\' ,;')


def discover_from_webpage(channel: dict, entry: dict, settings: dict) -> list[StreamCandidate]:
    url = entry['url']
    headers = {'User-Agent': settings.get('user_agent', 'IPTV-Maintainer')}
    timeout = settings.get('http_timeout_seconds', 12)
    found: list[str] = []
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        text = r.text
        found.extend(normalize_url(x) for x in M3U8_RE.findall(text))

        soup = BeautifulSoup(text, 'html.parser')
        for tag in soup.find_all(['source', 'video', 'iframe', 'script']):
            for attr in ['src', 'data-src']:
                value = tag.get(attr)
                if value and '.m3u8' in value:
                    found.append(normalize_url(value))
    except Exception as e:
        return [StreamCandidate(channel['id'], channel['name'], channel['group'], '', entry.get('region', 'OTHER'), 'webpage', url, False, error=str(e))]

    unique = []
    seen = set()
    for item in found:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return [StreamCandidate(channel['id'], channel['name'], channel['group'], u, entry.get('region', 'OTHER'), 'webpage', url) for u in unique]


def discover_from_youtube_search(channel: dict, entry: dict, settings: dict) -> list[StreamCandidate]:
    query = entry['query']
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--default-search', 'ytsearch3',
        '--match-filter', 'is_live | was_live',
        '--get-url',
        '--no-warnings',
        query,
    ]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
        urls = [line.strip() for line in proc.stdout.splitlines() if line.strip().startswith('http')]
    except Exception as e:
        return [StreamCandidate(channel['id'], channel['name'], channel['group'], '', entry.get('region', 'OTHER'), 'youtube_search', query, False, error=str(e))]
    return [StreamCandidate(channel['id'], channel['name'], channel['group'], u, entry.get('region', 'OTHER'), 'youtube_search', query) for u in urls]


def discover_from_m3u(channel: dict, entry: dict, settings: dict) -> list[StreamCandidate]:
    url = entry['url']
    headers = {'User-Agent': settings.get('user_agent', 'IPTV-Maintainer')}
    try:
        r = requests.get(url, headers=headers, timeout=settings.get('http_timeout_seconds', 12))
        r.raise_for_status()
        urls = [line.strip() for line in r.text.splitlines() if line.strip().startswith('http')]
    except Exception as e:
        return [StreamCandidate(channel['id'], channel['name'], channel['group'], '', entry.get('region', 'OTHER'), 'm3u', url, False, error=str(e))]
    return [StreamCandidate(channel['id'], channel['name'], channel['group'], u, entry.get('region', 'OTHER'), 'm3u', url) for u in urls]


def discover_channel(channel: dict, settings: dict) -> list[StreamCandidate]:
    if not channel.get('enabled', True):
        return []
    candidates: list[StreamCandidate] = []
    for entry in channel.get('entries', []):
        t = entry.get('type')
        if t == 'webpage':
            candidates.extend(discover_from_webpage(channel, entry, settings))
        elif t == 'youtube_search':
            candidates.extend(discover_from_youtube_search(channel, entry, settings))
        elif t == 'm3u':
            candidates.extend(discover_from_m3u(channel, entry, settings))
        elif t == 'direct':
            candidates.append(StreamCandidate(channel['id'], channel['name'], channel['group'], entry['url'], entry.get('region', 'OTHER'), 'direct', entry['url']))
    # keep only URL candidates, de-duplicate
    out: list[StreamCandidate] = []
    seen = set()
    for c in candidates:
        if not c.url:
            continue
        if c.url in seen:
            continue
        seen.add(c.url)
        out.append(c)
    return out
