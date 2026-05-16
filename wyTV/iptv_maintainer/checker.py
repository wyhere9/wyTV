from __future__ import annotations

import json
import subprocess
from dataclasses import asdict

from .models import StreamCandidate


def check_stream(candidate: StreamCandidate, settings: dict) -> StreamCandidate:
    if not candidate.url:
        candidate.playable = False
        candidate.error = candidate.error or 'empty url'
        return candidate

    timeout = int(settings.get('ffprobe_timeout_seconds', 15))
    cmd = [
        'ffprobe', '-v', 'error',
        '-rw_timeout', str(timeout * 1_000_000),
        '-show_entries', 'stream=codec_type,width,height,bit_rate',
        '-of', 'json',
        candidate.url,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if proc.returncode != 0:
            candidate.playable = False
            candidate.error = proc.stderr.strip()[:300] or 'ffprobe failed'
            return candidate
        data = json.loads(proc.stdout or '{}')
        streams = data.get('streams', [])
        video = next((s for s in streams if s.get('codec_type') == 'video'), None)
        candidate.playable = True
        if video:
            candidate.width = int(video['width']) if str(video.get('width', '')).isdigit() else None
            candidate.height = int(video['height']) if str(video.get('height', '')).isdigit() else None
            candidate.bitrate = int(video['bit_rate']) if str(video.get('bit_rate', '')).isdigit() else None
        candidate.score = score(candidate)
        return candidate
    except FileNotFoundError:
        candidate.playable = False
        candidate.error = 'ffprobe not installed'
        return candidate
    except Exception as e:
        candidate.playable = False
        candidate.error = str(e)[:300]
        return candidate


def score(candidate: StreamCandidate) -> float:
    s = 50.0 if candidate.playable else 0.0
    if candidate.height:
        if candidate.height >= 1080:
            s += 20
        elif candidate.height >= 720:
            s += 12
        elif candidate.height >= 480:
            s += 6
    if candidate.bitrate:
        s += min(candidate.bitrate / 1_000_000, 8)
    if 'youtube' in candidate.source_type:
        s += 2
    return s


def to_dict(candidate: StreamCandidate) -> dict:
    return asdict(candidate)
