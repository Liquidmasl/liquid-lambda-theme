"""Read the wallpaper COSMIC currently shows, for `lambda preview --wallpaper`."""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".jxl", ".bmp"}
_SOURCE = re.compile(r'source:\s*Path\("((?:[^"\\]|\\.)*)"\)')
_NAME = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _unescape(s: str) -> str:
    return re.sub(r"\\(.)", r"\1", s)


def config_dir() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "cosmic/com.system76.CosmicBackground/v1"


def _source(entry: Path) -> Path:
    m = _SOURCE.search(entry.read_text())
    if not m:
        raise ValueError(f"{entry.name}: the wallpaper is a colour or gradient, not an image; pass --wallpaper PATH")
    path = Path(_unescape(m.group(1)))
    if path.is_dir():  # slideshow: take the first image, as COSMIC's alphanumeric order would
        images = sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
        if not images:
            raise ValueError(f"{path}: slideshow folder has no images")
        path = images[0]
    return path


def current_wallpaper(output: str | None = None) -> Path:
    """The image on `output`, or with one wallpaper per screen, the one most screens show."""
    d = config_dir()
    if not d.is_dir():
        raise ValueError(f"no COSMIC background config at {d}; pass --wallpaper PATH")
    if output:
        entry = d / f"output.{output}"
        if not entry.is_file():
            known = sorted(p.name.removeprefix("output.") for p in d.glob("output.*"))
            raise ValueError(f"no wallpaper set for output {output!r}; known: {', '.join(known) or 'none'}")
        return _source(entry)
    if (d / "same-on-all").is_file() and (d / "same-on-all").read_text().strip() == "true":
        return _source(d / "all")
    listed = d / "backgrounds"
    names = [_unescape(n) for n in _NAME.findall(listed.read_text())] if listed.is_file() else []
    sources = [_source(d / f"output.{n}") for n in names if (d / f"output.{n}").is_file()]
    if not sources:
        return _source(d / "all")
    # most_common keeps first-seen order on ties, so the first listed screen wins those
    return Counter(sources).most_common(1)[0][0]
