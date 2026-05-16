from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StreamCandidate:
    channel_id: str
    channel_name: str
    group: str
    url: str
    region: str = 'OTHER'
    source_type: str = 'unknown'
    origin: str = ''
    playable: bool = False
    score: float = 0.0
    width: int | None = None
    height: int | None = None
    bitrate: int | None = None
    error: str = ''


@dataclass
class ChannelResult:
    channel_id: str
    name: str
    group: str
    candidates: list[StreamCandidate] = field(default_factory=list)
