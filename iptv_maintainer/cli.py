from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .checker import check_stream
from .config import ROOT, ensure_dirs, load_json
from .discovery import discover_channel
from .exporter import select_and_sort, write_m3u, write_report
from .models import StreamCandidate


def maintain() -> None:
    ensure_dirs()
    settings = load_json('config/settings.json')
    channels_cfg = load_json('config/channels.json')

    all_candidates: list[StreamCandidate] = []
    for channel in channels_cfg.get('channels', []):
        print(f'Discovering: {channel.get("name")}')
        discovered = discover_channel(channel, settings)
        print(f'  found {len(discovered)} candidate(s)')
        for candidate in discovered:
            checked = check_stream(candidate, settings)
            status = 'OK' if checked.playable else 'FAIL'
            print(f'  {status} {checked.region} {checked.url[:90]}')
            all_candidates.append(checked)

    selected = select_and_sort(all_candidates, settings)

    output_m3u = ROOT / settings.get('output_m3u', 'output/live.m3u')
    output_results = ROOT / settings.get('output_results', 'output/results.json')
    output_report = ROOT / settings.get('output_report', 'output/report.md')

    write_m3u(selected, output_m3u)
    write_report(all_candidates, selected, output_report)
    output_results.parent.mkdir(exist_ok=True)
    output_results.write_text(json.dumps([asdict(c) for c in all_candidates], ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'Wrote {output_m3u}')
    print(f'Wrote {output_results}')
    print(f'Wrote {output_report}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Maintain legal public IPTV M3U')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('maintain')
    args = parser.parse_args()
    if args.command in (None, 'maintain'):
        maintain()


if __name__ == '__main__':
    main()
