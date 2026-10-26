"""Cursor theme, built at apply time from vector sources recoloured to the palette.

The sources are other projects' SVG cursor themes (GPL / LGPL), fetched at a
pinned commit into ~/.cache, never vendored. `[cursor]` in palette.toml picks
a base theme and, per role, another source for single cursors, so styles can
be mixed. Every cursor is rendered at each size from its SVG, so it stays
sharp at any scale; names apps ask for are symlinks, taken from the base's
alias table.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import struct
import subprocess
import tomllib
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .color import Color
from .palette import Palette
from .web import GREY_CHROMA, role_for_hue

SIZES = (24, 32, 48, 64, 96)
NAME = "Lambda-Cursors"


@dataclass(frozen=True)
class Source:
    url: str
    commit: str
    licence: str


SOURCES = {
    "capitaine": Source("https://github.com/keeferrourke/capitaine-cursors.git",
                        "06c88433662a4004cf56a6e471b523a0a8880be0", "LGPL-3.0"),
    "bibata": Source("https://github.com/ful1e5/Bibata_Cursor.git",
                     "ddb09273cde49faeb6a32282660ff4293f52d6e0", "GPL-3.0"),
    "simp1e": Source("https://gitlab.com/cursors/simp1e.git",
                     "f8f8f3c09dd0aa31cc9bc5499c683aad025984be", "GPL-3.0"),
}


def cache_dir() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "liquid-lambda/cursor-sources"


def fetch(name: str) -> Path:
    """The source checked out at its pinned commit (cloned once, then reused)."""
    src = SOURCES[name]
    path = cache_dir() / f"{name}-{src.commit[:12]}"
    if not (path / ".git").is_dir():
        path.mkdir(parents=True, exist_ok=True)
        run = lambda *a: subprocess.run(["git", "-C", str(path), *a], check=True, capture_output=True)  # noqa: E731
        run("init", "-q")
        run("fetch", "-q", "--depth", "1", src.url, src.commit)
        run("checkout", "-q", "FETCH_HEAD")
    return path


# ── rendering ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Frame:
    size: int
    pixels: bytes  # premultiplied BGRA, size * size * 4
    xhot: int
    yhot: int
    delay: int = 0


def _image(svg: str, width: int, height: int):
    import cairosvg  # imported here: only apply needs it, and it needs libcairo
    from PIL import Image

    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=width, output_height=height)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def _pixels(im) -> bytes:
    # Xcursor wants premultiplied ARGB in little-endian words: Pillow's "RGBa" as BGRa bytes
    return im.convert("RGBa").tobytes("raw", "BGRa")


def _render(svg: str, size: int) -> bytes:
    return _pixels(_image(svg, size, size))


def _recolour(svg: str, mapping: dict[str, str], p: Palette | None = None) -> str:
    """Replace the source's placeholder colours; with p, move any other hex colour
    (spinners, badges) to the palette colour of its hue family, greys to muted."""
    for old, new in mapping.items():
        svg = re.sub(rf'(?<=["#:\s(]){re.escape(old)}(?![0-9A-Za-z])', new, svg, flags=re.I)
    if p is None:
        return svg
    keep = {v.lower().lstrip("#") for v in mapping.values()}

    def other(m: re.Match) -> str:
        h = m.group(1)
        full = "".join(c * 2 for c in h) if len(h) == 3 else h
        if full.lower() in keep:
            return m.group(0)
        L, C, hue = Color.hex(full).lch
        return (p.muted if C < GREY_CHROMA else p.roles[role_for_hue(hue)]).hex_str

    return re.sub(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F])", other, svg)


@dataclass(frozen=True)
class Look:
    """The two colours a cursor is drawn in."""
    body: Color
    outline: Color


# Each adapter: role -> callable(look, palette) -> list[Frame] at every size, or None if missing.
Adapter = Callable[[str, Look, Palette], list[Frame] | None]


def _capitaine(role: str, look: Look, p: Palette) -> list[Frame] | None:
    root = fetch("capitaine")
    svgdir, spec = root / "src/svg/dark", root / "src/config"
    m = {"1a1a1a": look.body.strip, "#fff": look.outline.hex_str, "#ffffff": look.outline.hex_str,
         "white": look.outline.hex_str}
    if (spec / f"static/{role}.spec").exists():
        xh, yh = (float(v) for v in (spec / f"static/{role}.spec").read_text().split()[:2])
        svg = _recolour((svgdir / f"{role}.svg").read_text(), m, p)
        return [Frame(s, _render(svg, s), round(xh * s / 24), round(yh * s / 24)) for s in SIZES]
    if (spec / f"animated/{role}.spec").exists():
        xh, yh, n, delay = (float(v) for v in (spec / f"animated/{role}.spec").read_text().split()[:4])
        frames = []
        for s in SIZES:
            for i in range(int(n)):
                svg = _recolour((svgdir / f"{role}-{i:02d}.svg").read_text(), m, p)
                frames.append(Frame(s, _render(svg, s), round(xh * s / 24), round(yh * s / 24), int(delay)))
        return frames
    return None


BIBATA_SCALE = 0.75
BIBATA_FILES = {"default": "left_ptr", "pointer": "hand2", "text": "xterm", "openhand": "hand1", "dnd-move": "grabbing"}


def _bibata(role: str, look: Look, p: Palette) -> list[Frame] | None:
    root = fetch("bibata")
    name = BIBATA_FILES.get(role, role)
    path = root / "svg/original" / f"{name}.svg"
    if not path.exists():
        return None
    cfg = tomllib.loads((root / "configs/normal/x.build.toml").read_text())["cursors"]
    entry = cfg.get(name, {})
    xh, yh = entry.get("x_hotspot", 128), entry.get("y_hotspot", 128)
    svg = _recolour(path.read_text(), {"#00FF00": look.body.hex_str, "#0000FF": look.outline.hex_str}, p)
    # Bibata draws about 1.4x as large as Capitaine: widen the viewBox so it
    # shrinks toward the top-left corner, where the hotspot sits
    span = 256 / BIBATA_SCALE
    svg = re.sub(r'viewBox="[^"]*"', f'viewBox="0 0 {span:g} {span:g}"', svg, count=1)
    return [Frame(s, _render(svg, s), round(xh * s / span), round(yh * s / span)) for s in SIZES]


SIMP1E_SLICES = {"wait": ("watch", (12, 12)), "progress": ("left_ptr_watch", None)}
SIMP1E_DELAY = 30  # ms per frame, 40 frames: 1.2 s a turn


def _simp1e(role: str, look: Look, p: Palette) -> list[Frame] | None:
    if role not in SIMP1E_SLICES:
        return None
    slice_name, hot = SIMP1E_SLICES[role]
    t = (fetch("simp1e") / "src/templates/cursors.svg").read_text()
    ink = "{http://www.inkscape.org/namespaces/inkscape}label"
    boxes = {}
    for r in ET.fromstring(t).iter("{http://www.w3.org/2000/svg}rect"):
        lab = r.get(ink) or ""
        if lab.startswith(slice_name + "_"):
            x, y, w, h = (float(r.get(k)) for k in ("x", "y", "width", "height"))
            boxes[lab] = (x + 28, y + 56, w, h)  # the slices layer sits at translate(28,56)
    t = t.replace("#550055", "none").replace("#505050", "none")
    t = re.sub(r"<text[\s\S]*?</text>", "", t)
    # template colours (simp1e/template_colors.txt) -> palette
    t = _recolour(t, {
        "#ffffff": "#000000",                 # shadow
        "#ff0000": look.outline.hex_str,      # cursor_border
        "#00ff00": look.body.hex_str,         # default_cursor_bg (the arrow of progress)
        "#aa0000": look.body.hex_str,         # spinner_bg
        "#ff00aa": p.second.hex_str,          # spinner_fg1: both strips in the amber
        "#ffaa00": p.second.hex_str,          # spinner_fg2
    })
    vw, vh = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', t).groups())
    frames = []
    for s in SIZES:
        k = s / 24  # the template draws every cursor on a 24 unit grid
        sheet = _image(t, round(vw * k), round(vh * k))  # once per size, then cut out each frame
        for lab in sorted(boxes):
            x, y, w, h = boxes[lab]
            px = _pixels(sheet.crop((round(x * k), round(y * k), round(x * k) + s, round(y * k) + s)))
            xh, yh = (round(hot[0] * k), round(hot[1] * k)) if hot else _tip(px, s)
            frames.append(Frame(s, px, xh, yh, SIMP1E_DELAY))
    return frames


def _tip(pixels: bytes, size: int) -> tuple[int, int]:
    """Top-left-most opaque pixel: the click point of an arrow."""
    best = (0, 0, 10**9)
    for i in range(size * size):
        if pixels[4 * i + 3] > 128:
            x, y = i % size, i // size
            if x + y < best[2]:
                best = (x, y, x + y)
    return best[0], best[1]


def _compose(arrow: list[Frame], spinner: list[Frame]) -> list[Frame]:
    """Arrow plus busy: the spinner at 60% in the lower right, one frame per spinner frame."""
    from PIL import Image

    out = []
    for f in spinner:
        a = next(x for x in arrow if x.size == f.size)
        im = Image.frombytes("RGBa", (a.size, a.size), a.pixels, "raw", "BGRa").convert("RGBA")
        spin = Image.frombytes("RGBa", (f.size, f.size), f.pixels, "raw", "BGRa").convert("RGBA")
        small = round(f.size * 0.6)
        im.alpha_composite(spin.resize((small, small), Image.LANCZOS), (f.size - small, f.size - small))
        out.append(Frame(f.size, _pixels(im), a.xhot, a.yhot, f.delay))
    return out


ADAPTERS: dict[str, Adapter] = {"capitaine": _capitaine, "bibata": _bibata, "simp1e": _simp1e}


# ── Xcursor files ───────────────────────────────────────────────────────────


def xcursor(frames: list[Frame]) -> bytes:
    """An Xcursor file (see Xcursor(3)): a table of contents, then one image chunk per frame."""
    header = 16
    toc = 12 * len(frames)
    chunks, offsets, pos = [], [], header + toc
    for f in frames:
        chunk = struct.pack("<IIIIIIIII", 36, 0xFFFD0002, f.size, 1, f.size, f.size, f.xhot, f.yhot, f.delay) + f.pixels
        offsets.append(pos)
        chunks.append(chunk)
        pos += len(chunk)
    out = struct.pack("<4sIII", b"Xcur", header, 0x10000, len(frames))
    out += b"".join(struct.pack("<III", 0xFFFD0002, f.size, off) for f, off in zip(frames, offsets))
    return out + b"".join(chunks)


# Names some apps ask for that the base's alias table lacks -> base file name
EXTRA_ALIASES = {
    "pointing_hand": "pointer", "closedhand": "dnd-move", "half-busy": "progress", "forbidden": "not-allowed",
    "split_v": "col-resize", "split_h": "row-resize", "cross": "crosshair", "plus": "cell", "link": "alias",
    "e-resize": "size_hor", "w-resize": "size_hor", "ew-resize": "size_hor", "n-resize": "size_ver",
    "s-resize": "size_ver", "ns-resize": "size_ver", "ne-resize": "size_bdiag", "sw-resize": "size_bdiag",
    "nesw-resize": "size_bdiag", "nw-resize": "size_fdiag", "se-resize": "size_fdiag", "nwse-resize": "size_fdiag",
    "move": "dnd-move", "dnd-none": "dnd-move", "all-scroll": "fleur", "size_all": "fleur", "ibeam": "text",
    "zoom-in": "cell", "zoom-out": "cell",
}


def validate(recipe: dict[str, str]) -> None:
    """Fail on a [cursor] recipe that names an unknown source, before anything is fetched."""
    if recipe.get("base", "capitaine") != "capitaine":
        raise ValueError("[cursor] base: only capitaine provides a full cursor set so far")
    for role, source in recipe.items():
        if role == "base" or (role == "progress" and source == "compose"):
            continue
        if source not in ADAPTERS:
            raise ValueError(f"[cursor] {role} = {source!r}: unknown source; known: {', '.join(ADAPTERS)}")


def build(p: Palette, recipe: dict[str, str], out: Path) -> list[str]:
    """Write the cursor theme to out (replacing it); returns the roles taken from each non-base source."""
    validate(recipe)
    base = recipe.get("base", "capitaine")
    looks = {"default": Look(p.lead, p.bg), "busy": Look(p.surface2, p.lead)}
    root = fetch(base)
    roles = (root / "src/static-cursor-list").read_text().split() + (root / "src/animated-cursor-list").read_text().split()
    cursors = out / "cursors"
    if out.exists():
        shutil.rmtree(out)
    cursors.mkdir(parents=True)
    mixed: list[str] = []
    built: dict[str, list[Frame]] = {}
    progress_compose = recipe.get("progress") == "compose"
    for role in roles:
        if role == "progress" and progress_compose:
            continue
        source = recipe.get(role, base)
        look = looks["busy"] if role in ("wait", "progress") and source == "simp1e" else looks["default"]
        frames = ADAPTERS[source](role, look, p)
        if frames is None:
            raise ValueError(f"[cursor] {role} = {source!r}: {source} has no {role} cursor")
        (cursors / role).write_bytes(xcursor(frames))
        if source != base:
            mixed.append(f"{role} from {source}")
        built[role] = frames
    if progress_compose:
        (cursors / "progress").write_bytes(xcursor(_compose(built["default"], built["wait"])))
        mixed.append("progress composed from default + wait")
    links = {}
    for line in (root / "src/cursor-aliases").read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            links[parts[0]] = parts[1]
    links |= {k: v for k, v in EXTRA_ALIASES.items() if k not in links}
    for link, target in sorted(links.items()):
        if (cursors / target).exists() and not (cursors / link).exists():
            (cursors / link).symlink_to(target)
    used = {base, *recipe.values()} & set(SOURCES)
    licences = ", ".join(f"{n} ({SOURCES[n].licence})" for n in sorted(used))
    (out / "index.theme").write_text(
        f"[Icon Theme]\nName={NAME}\nComment=Liquid Lambda cursors from {licences}, recoloured to the palette\n")
    return mixed
