"""Kvantum (Qt apps such as Dolphin): KvArcDark recoloured to the palette.

KvArcDark ships with Kvantum under the GPL, so the repo carries only this
recipe and `lambda apply` builds the theme on the machine from the installed
copy: Arc's blue-greys move onto the palette's warm grey ramp, Arc's blue onto
the lead colour, corners are squared and windows are translucent.
"""

from __future__ import annotations

import colorsys
import re
from pathlib import Path

from .color import Color
from .palette import Palette

SOURCE = Path("/usr/share/Kvantum/KvArcDark")
NAME = "Lambda"
ARC_WINDOW_L = 0.257  # HLS lightness of Arc's window grey #383c4a


def _hls_l(c: Color) -> float:
    return colorsys.rgb_to_hls(c.r / 255, c.g / 255, c.b / 255)[1]


def _recolour(p: Palette):
    bg_l, lead_l = _hls_l(p.bg), _hls_l(p.lead)

    def grey(l: float) -> Color:
        # Arc's window grey lands on bg; lighter tones spread up to the text colour
        if l <= ARC_WINDOW_L:
            return p.bg.mix(p.lead_ink, 1 - l / ARC_WINDOW_L)
        return p.bg.mix(p.text, min(1.0, (l - ARC_WINDOW_L) / (0.9 - ARC_WINDOW_L)))

    def accent(l: float) -> Color:
        if l <= lead_l:
            return p.lead.mix(p.bg, (lead_l - l) / max(lead_l - bg_l, 1e-6))
        return p.lead.mix(p.text, (l - lead_l) / max(1 - lead_l, 1e-6))

    def sub(m: re.Match) -> str:
        v = m.group(1)
        r, g, b = (int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        if s > 0.4 and 190 / 360 <= h <= 235 / 360:
            return accent(l).hex_str
        if s > 0.4:  # other accents (purple links, reds) stay
            return m.group(0)
        return grey(l).hex_str

    return lambda text: re.sub(r"#([0-9a-fA-F]{6})(?![0-9a-fA-F])", sub, text)


def _set_keys(cfg: str, section: str, values: dict[str, str]) -> str:
    m = re.search(rf"^\[{re.escape(section)}\]\n(.*?)(?=^\[|\Z)", cfg, re.S | re.M)
    if not m:
        return cfg.rstrip() + f"\n\n[{section}]\n" + "".join(f"{k}={v}\n" for k, v in values.items())
    block = m.group(1)
    for key, val in values.items():
        pattern = rf"^{re.escape(key)}=.*$"
        line = f"{key}={val}"
        block = re.sub(pattern, line, block, flags=re.M) if re.search(pattern, block, re.M) else block + line + "\n"
    return cfg[: m.start(1)] + block + cfg[m.end(1):]


def build(p: Palette, source: Path = SOURCE) -> dict[str, str]:
    """{file name: content} of the Lambda Kvantum theme."""
    recolour = _recolour(p)
    svg = re.sub(r'\s(rx|ry)="[^"]*"', "", recolour((source / "KvArcDark.svg").read_text()))
    cfg = recolour((source / "KvArcDark.kvconfig").read_text())
    cfg = _set_keys(cfg, "%General", {
        "comment": "KvArcDark recoloured to the Liquid Lambda palette, square corners (lambda apply)",
        "translucent_windows": "true",
        "blurring": "true",
        "popup_blurring": "true",
        "reduce_window_opacity": "15",
        "reduce_menu_opacity": "20",
    })
    cfg = _set_keys(cfg, "GeneralColors", {
        "window.color": p.bg.hex_str,
        "base.color": p.bg.hex_str,
        "alt.base.color": "#ffffff0a",  # translucent so striped rows don't block the see-through view
        "button.color": p.surface2.hex_str,
        "light.color": p.line.hex_str,
        "mid.light.color": p.surface2.hex_str,
        "dark.color": "black",
        "mid.color": p.lead_ink.hex_str,
        "highlight.color": p.lead.hex_str,
        "inactive.highlight.color": p.lead.mix(p.bg, 0.3).hex_str,
        "text.color": p.text.hex_str,
        "window.text.color": p.text.hex_str,
        "button.text.color": p.text.hex_str,
        "disabled.text.color": p.muted.hex_str,
        "tooltip.text.color": p.text.hex_str,
        "highlight.text.color": p.lead_ink.hex_str,
        "link.color": p.link.hex_str,
        "link.visited.color": p.magenta.hex_str,
        "progress.indicator.text.color": p.lead_ink.hex_str,
    })
    cfg = _set_keys(cfg, "Hacks", {"transparent_dolphin_view": "true", "blur_translucent": "true"})
    return {f"{NAME}.svg": svg, f"{NAME}.kvconfig": cfg}
