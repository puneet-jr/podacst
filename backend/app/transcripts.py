"""Untrusted transcript parsing and exact-span chunking; no source instructions execute."""
from dataclasses import dataclass, field
from datetime import date, datetime
from hashlib import sha256
from math import ceil
from pathlib import PurePosixPath
import re
import unicodedata
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

import yaml
from yaml.tokens import AliasToken, AnchorToken

SOURCE_URL = "https://github.com/ChatPRD/lennys-podcast-transcripts"
PARSER_VERSION = "transcript-v1"
CHUNK_VERSION = "sentence-turn-v1-550-700-80"
STAMP = r"\d{1,3}:\d{2}(?::\d{2})?"
PAREN = re.compile(rf"^(?P<speaker>[^\r\n():]{{1,100}}?)?[ \t]*\((?P<time>{STAMP})\):[ \t]*", re.M)
BRACKET = re.compile(rf"^\[(?P<time>{STAMP})\][ \t]*(?:(?P<speaker>[^\r\n:]{{1,100}}):[ \t]*)?", re.M)
SPEAKER_ONLY = re.compile(r"^(?P<speaker>[A-Z][A-Za-z .’'\-]{0,79}):[ \t]*(?:\r?\n|$)", re.M)
SPONSOR = re.compile(r"\b(?:brought to you by|sponsored by|our sponsors?|today['’]s sponsors?|episode['’]s brought to you by)\b", re.I)


class ParseError(ValueError):
    pass


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ParseError("invalid_or_duplicate_metadata_key")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


@dataclass
class Turn:
    start: int
    end: int
    speaker: str | None
    seconds: int | None
    sponsor: bool


@dataclass
class Episode:
    path: str
    source_hash: str
    original: str
    guest: str | None
    title: str
    published_on: date | None
    video_url: str | None
    metadata: dict
    turns: list[Turn]
    warnings: list[str] = field(default_factory=list)

    @property
    def id(self):
        return uuid5(NAMESPACE_URL, SOURCE_URL + "/" + self.path)


@dataclass
class Chunk:
    ordinal: int
    start: int
    end: int
    original: str
    search_text: str
    speakers: list[str]
    start_seconds: int | None
    end_seconds: int | None
    estimated_tokens: int
    line_start: int
    line_end: int
    sponsor: bool


def timestamp(value):
    parts = [int(x) for x in value.split(":")]
    if len(parts) not in (2, 3) or parts[-1] >= 60 or (len(parts) == 3 and parts[-2] >= 60):
        raise ParseError("invalid_timestamp")
    return sum(number * 60 ** power for power, number in enumerate(reversed(parts)))


def parse_transcript(data: bytes, path: str) -> Episode:
    if not 0 < len(data) <= 3_000_000:
        raise ParseError("source_size_out_of_bounds")
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ParseError("invalid_source_path")
    try:
        original = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParseError("invalid_utf8") from exc
    warnings, metadata = [], {}
    begin = 1 if original.startswith("\ufeff") else 0
    opening = re.match(r"---[ \t]*\r?\n", original[begin:])
    body = begin
    if opening:
        front_start = begin + opening.end()
        closing = re.compile(r"^---[ \t]*(?:\r?\n|$)", re.M).search(original, front_start)
        if closing is None or closing.start() - front_start > 65536:
            raise ParseError("unclosed_or_oversized_frontmatter")
        front = original[front_start:closing.start()]
        try:
            tokens = list(yaml.scan(front, Loader=UniqueSafeLoader))
            if len(tokens) > 10000 or any(isinstance(t, (AliasToken, AnchorToken)) for t in tokens):
                raise ParseError("yaml_alias_or_size_not_allowed")
            metadata = yaml.load(front, Loader=UniqueSafeLoader) or {}
        except yaml.YAMLError as exc:
            raise ParseError("invalid_yaml_frontmatter") from exc
        if not isinstance(metadata, dict):
            raise ParseError("metadata_must_be_mapping")
        body = closing.end()
    else:
        warnings.append("missing_frontmatter")
    section = re.compile(r"^##\s+Transcript\s*\r?$", re.M | re.I).search(original, body)
    if section:
        body = section.end()
    else:
        warnings.append("missing_transcript_heading")
    def value(key):
        item = metadata.get(key)
        return item.strip() if isinstance(item, str) and item.strip() else None
    heading = re.compile(r"^#\s+(.+)$", re.M).search(original, begin)
    title = value("title") or (heading.group(1).strip() if heading else relative.parent.name.replace("-", " "))
    guest = value("guest")
    if not guest: warnings.append("missing_guest")
    if not value("title"): warnings.append("missing_title")
    if guest:
        names = re.findall(r"[a-z]+", guest.casefold())
        significant = [n for n in names if n not in {"live", "and", "with"}]
        if significant and not all(n in title.casefold() for n in significant):
            warnings.append("guest_title_mismatch_review_required")
    published = metadata.get("publish_date")
    if isinstance(published, datetime): published = published.date()
    if isinstance(published, str):
        try: published = date.fromisoformat(published)
        except ValueError: published = None; warnings.append("invalid_publish_date")
    if not isinstance(published, date): published = None
    url = value("youtube_url")
    if url:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname not in {"www.youtube.com", "youtube.com", "youtu.be"} or parsed.username or parsed.password:
            url = None; warnings.append("unsafe_video_url")
    marks = []
    for pattern in (PAREN, BRACKET):
        for match in pattern.finditer(original, body):
            try: seconds = timestamp(match.group("time"))
            except ParseError: warnings.append("invalid_timestamp"); continue
            marks.append((match.start(), match.end(), (match.group("speaker") or "").strip() or None, seconds))
    if not marks:
        marks = [(m.start(), m.end(), m.group("speaker").strip(), None) for m in SPEAKER_ONLY.finditer(original, body)]
        warnings.append("missing_timestamps")
    marks.sort()
    if not marks:
        marks = [(body, body, None, None)]
        warnings.append("unstructured_transcript")
    turns, speaker, previous_time = [], None, None
    for i, (_header, start, name, seconds) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(original)
        speaker = name or speaker
        if seconds is not None and previous_time is not None and seconds < previous_time:
            warnings.append("non_monotonic_timestamp")
        if seconds is not None: previous_time = seconds
        if original[start:end].strip():
            turns.append(Turn(start, end, speaker, seconds, bool(SPONSOR.search(original[start:end]))))
    if not turns: raise ParseError("empty_transcript")
    return Episode(path, sha256(data).hexdigest(), original, guest, title, published, url, metadata, turns, sorted(set(warnings)))


def estimate_tokens(text):
    """UTF-8 bytes/4 heuristic, not the embedding model's tokenizer."""
    return max(ceil(len(text.encode("utf-8")) / 4), len(text.split()))


def split_long_span(text, start, end, maximum):
    while start < end:
        if estimate_tokens(text[start:end]) <= maximum:
            yield start, end
            break
        low, high = start + 1, end
        while low < high:
            middle = (low + high + 1) // 2
            if estimate_tokens(text[start:middle]) <= maximum: low = middle
            else: high = middle - 1
        boundary = text.rfind(" ", start + 1, low + 1)
        cut = boundary + 1 if boundary > start else low
        yield start, cut
        start = cut


def chunk_episode(episode: Episode, target=550, maximum=700, overlap=80) -> list[Chunk]:
    if not 100 <= target <= maximum <= 700 or not 0 <= overlap < target:
        raise ValueError("invalid_chunk_bounds")
    raw, atoms = episode.original, []
    for turn in episode.turns:
        start = turn.start
        content = raw[turn.start:turn.end]
        for match in re.finditer(r'(?<=[.!?])\s+(?=[A-Z0-9"“])|\n[ \t]*\r?\n', content):
            end = turn.start + match.end()
            atoms.extend(split_long_span(raw, start, end, maximum - 50))
            start = end
        if start < turn.end: atoms.extend(split_long_span(raw, start, turn.end, maximum - 50))
    chunks, i = [], 0
    while i < len(atoms):
        j = i
        while j < len(atoms) and estimate_tokens(raw[atoms[i][0]:atoms[j][1]]) <= maximum:
            j += 1
            if estimate_tokens(raw[atoms[i][0]:atoms[j - 1][1]]) >= target: break
        if j == i: raise ParseError("chunk_bound_exceeded")
        start, end = atoms[i][0], atoms[j - 1][1]
        exact = raw[start:end]
        turns = [t for t in episode.turns if t.start < end and t.end > start]
        times = [t.seconds for t in turns if t.seconds is not None]
        speakers = list(dict.fromkeys(t.speaker for t in turns if t.speaker))
        chunks.append(Chunk(len(chunks), start, end, exact, " ".join(unicodedata.normalize("NFC", exact).split()), speakers,
                            min(times) if times else None, max(times) if times else None, estimate_tokens(exact),
                            raw.count("\n", 0, start) + 1, raw.count("\n", 0, max(start, end - 1)) + 1, any(t.sponsor for t in turns)))
        if j == len(atoms): break
        next_i = j
        while next_i > i + 1 and estimate_tokens(raw[atoms[next_i - 1][0]:atoms[j - 1][1]]) <= overlap:
            next_i -= 1
        i = next_i
    return chunks
