"""Userstyles that move a site's own dark theme onto the palette.

The input is a snapshot of the colour custom properties a site defines
(data/web/<site>.json, written by tools/snapshot_web.py). Each colour is
mapped by what it is rather than by name, so hundreds of design tokens need
no hand mapping: greys land on the palette's grey ramp at the same place
between the site's own background and text, accents keep their lightness
and take the palette colour of their hue family, alpha is kept.

Stylus updates a userstyle from its @updateURL only when @version grows, so
each site's version counter (data/web/versions.json) goes up whenever its
generated declarations change.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .color import Color
from .palette import Palette

REPO_RAW = "https://raw.githubusercontent.com/Liquidmasl/liquid-lambda-theme/master"
GREY_CHROMA = 0.035  # below this OKLCH chroma a colour counts as a grey


@dataclass(frozen=True)
class Site:
    title: str
    domains: tuple[str, ...]
    bg: str  # the site's own page background and body text, anchoring the grey ramp
    fg: str


SITES = {
    "github": Site("GitHub", ("github.com", "gist.github.com"), "--bgColor-default", "--fgColor-default"),
    "reddit": Site("Reddit", ("reddit.com",), "--color-neutral-background", "--color-neutral-content"),
    "youtube": Site("YouTube", ("youtube.com",), "--yt-sys-color-baseline--base-background",
                    "--yt-sys-color-baseline--text-primary"),
}

# OKLCH hue ranges of the source accent -> palette role taking its place
HUE_ROLES = ((30, "err"), (105, "second"), (180, "ok"), (290, "lead"), (345, "magenta"), (360, "err"))

_HEX = re.compile(r"^#([0-9a-fA-F]{3,8})$")
_RGB = re.compile(r"^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$")


def parse(value: str) -> tuple[Color, float] | None:
    """(colour, alpha) of a CSS hex or rgb()/rgba() value."""
    v = value.strip()
    if m := _HEX.match(v):
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return Color.hex(h[:6]), alpha
    if m := _RGB.match(v):
        r, g, b = (min(255, round(float(x))) for x in m.group(1, 2, 3))
        a = m.group(4)
        alpha = 1.0 if a is None else float(a[:-1]) / 100 if a.endswith("%") else float(a)
        return Color(r, g, b), alpha
    return None


def _role_for_hue(h: float) -> str:
    return next(role for limit, role in HUE_ROLES if h < limit)


def remap(colour: Color, site_bg: Color, site_fg: Color, p: Palette) -> Color:
    L, C, h = colour.lch
    if C < GREY_CHROMA:
        lo, hi = site_bg.lch[0], site_fg.lch[0]
        t = (L - lo) / (hi - lo) if hi != lo else 0.0
        if t < 0:  # darker than the page (headers, insets): a little toward black
            return p.bg.mix(Color(0, 0, 0), min(0.5, -t * 1.5))
        if t > 1:  # brighter than the text: toward white
            return p.text.mix(Color(255, 255, 255), min(1.0, (t - 1) * 4))
        return p.bg.mix(p.text, t)
    role = p.roles[_role_for_hue(h)]
    _, rc, rh = role.lch
    # keep the site's lightness (its contrast design), take the palette hue; a
    # muted source stays muted, a vivid one goes as far as the palette colour
    return Color.oklch(L, rc * min(1.0, max(0.3, C / 0.1)), rh)


def css(colour: Color, alpha: float) -> str:
    return colour.hex_str if alpha >= 0.999 else f"{colour.hex_str}{round(alpha * 255):02x}"


def declarations(root: Path, name: str, p: Palette) -> list[tuple[str, str]]:
    site = SITES[name]
    tokens = json.loads((root / "data/web" / f"{name}.json").read_text())
    bg, fg = parse(tokens[site.bg])[0], parse(tokens[site.fg])[0]
    out = []
    for var, value in tokens.items():
        parsed = parse(value)
        if parsed:
            out.append((var, css(remap(parsed[0], bg, fg, p), parsed[1])))
    return out


def userstyle(root: Path, name: str, p: Palette) -> dict[str, object]:
    """Everything the web template needs for one site."""
    decls = declarations(root, name, p)
    digest = hashlib.sha256(repr(decls).encode()).hexdigest()[:16]
    versions = json.loads((root / "data/web/versions.json").read_text()) if (root / "data/web/versions.json").exists() else {}
    seen = versions.get(name, {"n": 0, "hash": ""})
    n = seen["n"] if seen["hash"] == digest else seen["n"] + 1
    site = SITES[name]
    return {
        "name": name, "title": site.title, "domains": site.domains, "decls": decls,
        "version": f"1.0.{n}", "update_url": f"{REPO_RAW}/web/{name}.user.css",
        "_state": {"n": n, "hash": digest},
    }


def record_versions(root: Path, p: Palette) -> bool:
    """Store each site's version counter; True when it changed (build only)."""
    path = root / "data/web/versions.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    new = {name: userstyle(root, name, p)["_state"] for name in SITES}
    if new != old:
        path.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
        return True
    return False
