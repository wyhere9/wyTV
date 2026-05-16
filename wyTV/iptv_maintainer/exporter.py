from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .models import StreamCandidate


def region_rank(region: str, settings: dict) -> int:
    priority = settings.get('region_priority', ['CN', 'HK', 'US', 'OTHER'])
    region = region if region in priority else 'OTHER'
    return priority.index(region) if region in priority else len(priority)


def select_and_sort(candidates: list[StreamCandidate], settings: dict) -> dict[str, list[StreamCandidate]]:
    by_channel: dict[str, list[StreamCandidate]] = defaultdict(list)
    for c in candidates:
        if c.playable:
            by_channel[c.channel_id].append(c)

    selected: dict[str, list[StreamCandidate]] = {}
    max_per_region = int(settings.get('max_sources_per_region', 2))
    max_per_channel = int(settings.get('max_sources_per_channel', 6))

    for cid, items in by_channel.items():
        grouped: dict[str, list[StreamCandidate]] = defaultdict(list)
        for c in items:
            grouped[c.region].append(c)
        ordered: list[StreamCandidate] = []
        for region in settings.get('region_priority', ['CN', 'HK', 'US', 'OTHER']):
            region_items = sorted(grouped.get(region, []), key=lambda x: x.score, reverse=True)
            ordered.extend(region_items[:max_per_region])
        # append unknown regions not listed
        extras = []
        for region, region_items in grouped.items():
            if region not in settings.get('region_priority', []):
                extras.extend(sorted(region_items, key=lambda x: x.score, reverse=True)[:max_per_region])
        ordered.extend(extras)
        selected[cid] = ordered[:max_per_channel]
    return selected


def write_m3u(selected: dict[str, list[StreamCandidate]], output_path: str | Path) -> None:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = ['#EXTM3U']
    for _, items in selected.items():
        for c in items:
            logo = ''
            lines.append(f'#EXTINF:-1 group-title="{c.group}" tvg-id="{c.channel_id}" tvg-name="{c.channel_name}"{logo},{c.channel_name} [{c.region}]')
            lines.append(c.url)
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_report(all_candidates: list[StreamCandidate], selected: dict[str, list[StreamCandidate]], output_path: str | Path) -> None:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    playable = sum(1 for c in all_candidates if c.playable)
    total = len([c for c in all_candidates if c.url])
    lines = [
        '# IPTV Maintainer Report',
        '',
        f'- Candidates discovered: {total}',
        f'- Playable candidates: {playable}',
        f'- Channels exported: {len(selected)}',
        '',
        '## Exported Channels',
        ''
    ]
    for cid, items in selected.items():
        if not items:
            continue
        lines.append(f'### {items[0].channel_name}')
        for c in items:
            lines.append(f'- {c.region} | score={c.score:.1f} | {c.source_type} | {c.url[:120]}')
        lines.append('')
    p.write_text('\n'.join(lines), encoding='utf-8')
