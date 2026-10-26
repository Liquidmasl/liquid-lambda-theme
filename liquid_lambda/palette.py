"""palette.toml inputs -> the named roles every template is written against.

build() is mirrored in templates/tuner/engine.js (buildPalette); change both
together, tests/test_parity.py fails when they drift.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

from .color import Color

# Hue of the greys per tint; cool follows the cyan hue
TINT_HUE = {"warm": 28.0, "neutral": 0.0}
MAX_TINT_CHROMA = 0.028

# (lightness, chroma) of the two accents at full strength, from the wallpaper
CYAN = (0.83, 0.145)
AMBER = (0.74, 0.155)

# Grey ramp: role -> (lightness, share of the tint chroma)
NEUTRALS = {
    "bg": (0.165, 1.0),
    "surface1": (0.2, 1.0),
    "surface2": (0.24, 1.0),
    "surface3": (0.29, 1.0),
    "line": (0.37, 0.9),
    "dim": (0.54, 0.7),
    "muted": (0.64, 0.6),
    "sub": (0.78, 0.45),
    "text": (0.91, 0.3),
}

# Roles a [pin] may override. Aliases (cyan, amber, warn, link, hint, ansi) are
# derived after pins, so pinning lead also moves the focus ring and the links.
BASE_ROLES = (
    *NEUTRALS,
    "lead", "lead_ink", "second", "second_ink",
    "ok", "err", "yellow", "blue", "magenta",
    "err_bright", "ok_bright", "amber_bright", "blue_bright", "magenta_bright", "cyan_bright",
)


DEFAULT_CURSOR = {"base": "capitaine", "default": "bibata", "wait": "simp1e", "progress": "compose"}


@dataclass(frozen=True)
class Settings:
    lead: str = "cyan"
    tint: str = "warm"
    tint_strength: float = 55
    second_loudness: float = 70
    cyan_hue: float = 212
    amber_hue: float = 66
    lead_chroma: float = 85
    pin: dict[str, str] = field(default_factory=dict)
    # cursor recipe: base theme, then role = source for single cursors (see cursor.py)
    cursor: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_CURSOR))

    def __post_init__(self) -> None:
        checks = {
            "lead": self.lead in ("cyan", "amber"),
            "tint": self.tint in ("warm", "neutral", "cool"),
            "tint_strength": 0 <= self.tint_strength <= 100,
            "second_loudness": 20 <= self.second_loudness <= 100,
            "cyan_hue": 180 <= self.cyan_hue <= 235,
            "amber_hue": 35 <= self.amber_hue <= 85,
            "lead_chroma": 40 <= self.lead_chroma <= 100,
        }
        bad = [k for k, ok in checks.items() if not ok]
        if bad:
            raise ValueError(f"palette.toml: out of range: {', '.join(bad)} (see the comments in palette.toml)")
        unknown = sorted(set(self.pin) - set(BASE_ROLES))
        if unknown:
            raise ValueError(f"palette.toml: [pin] has unknown roles {unknown}; pinnable: {', '.join(BASE_ROLES)}")

    @classmethod
    def load(cls, path: Path) -> Settings:
        data = tomllib.loads(path.read_text())
        known = {f.name for f in fields(cls)} - {"pin", "cursor"}
        section = data.get("palette", {})
        unknown = sorted(set(section) - known)
        if unknown:
            raise ValueError(f"{path}: unknown [palette] keys {unknown}")
        return cls(**section, pin=data.get("pin", {}), cursor={**DEFAULT_CURSOR, **data.get("cursor", {})})


@dataclass(frozen=True)
class Palette:
    roles: dict[str, Color]
    ansi: tuple[Color, ...]

    def __getattr__(self, name: str) -> Color:
        try:
            return self.roles[name]
        except KeyError:
            raise AttributeError(name) from None


def build(s: Settings) -> Palette:
    tint_hue = s.cyan_hue if s.tint == "cool" else TINT_HUE[s.tint]
    tint_chroma = 0.0 if s.tint == "neutral" else s.tint_strength / 100 * MAX_TINT_CHROMA

    def grey(L: float, share: float = 1.0) -> Color:
        return Color.oklch(L, tint_chroma * share, tint_hue)

    cyan_full = (*CYAN, s.cyan_hue)
    amber_full = (*AMBER, s.amber_hue)
    lead_v, second_v = (cyan_full, amber_full) if s.lead == "cyan" else (amber_full, cyan_full)
    lead_k, second_k = s.lead_chroma / 100, s.second_loudness / 100

    base: dict[str, Color] = {role: grey(L, share) for role, (L, share) in NEUTRALS.items()}
    base |= {
        "lead": Color.oklch(lead_v[0], lead_v[1] * lead_k, lead_v[2]),
        # a quieter second colour also drops a little in lightness
        "second": Color.oklch(second_v[0] - (1 - second_k) * 0.08, second_v[1] * second_k, second_v[2]),
        "lead_ink": grey(0.17),
        "second_ink": grey(0.17),
        "ok": Color.oklch(0.78, 0.1, 150),
        "err": Color.oklch(0.68, 0.17, 25),
        # warnings when amber leads, so they stay apart from the accent
        "yellow": Color.oklch(0.86, 0.13, 98),
        "blue": Color.oklch(0.72, 0.1, 255),
        "magenta": Color.oklch(0.72, 0.1, 330),
        "err_bright": Color.oklch(0.76, 0.16, 25),
        "ok_bright": Color.oklch(0.85, 0.1, 150),
        "amber_bright": Color.oklch(0.82, 0.14, s.amber_hue),
        "blue_bright": Color.oklch(0.8, 0.09, 255),
        "magenta_bright": Color.oklch(0.8, 0.09, 330),
        "cyan_bright": Color.oklch(0.9, 0.11, s.cyan_hue),
    }
    base |= {role: Color.hex(v) for role, v in s.pin.items()}

    r = dict(base)
    r["cyan"], r["amber"] = (r["lead"], r["second"]) if s.lead == "cyan" else (r["second"], r["lead"])
    r["warn"] = r["amber"] if s.lead == "cyan" else r["yellow"]
    r["link"] = r["cyan"]
    r["hint"] = r["lead"]

    ansi = (
        r["surface2"], r["err"], r["ok"], r["amber"], r["blue"], r["magenta"], r["cyan"], r["sub"],
        r["dim"], r["err_bright"], r["ok_bright"], r["amber_bright"],
        r["blue_bright"], r["magenta_bright"], r["cyan_bright"], r["text"],
    )
    return Palette(roles=r, ansi=ansi)


# (role, background role, minimum ratio): text-like roles 4.5:1, UI marks 3:1
CONTRAST_GATES = (
    ("text", "bg", 4.5),
    ("sub", "bg", 4.5),
    ("muted", "bg", 4.5),
    ("dim", "bg", 3.0),
    ("text", "surface2", 4.5),
    ("muted", "surface2", 3.0),
    ("lead", "bg", 3.0),
    ("second", "bg", 3.0),
    ("ok", "bg", 4.5),
    ("warn", "bg", 4.5),
    ("err", "bg", 4.5),
    ("link", "bg", 4.5),
    ("lead_ink", "lead", 4.5),
    ("second_ink", "second", 4.5),
)


def contrast_failures(p: Palette) -> list[str]:
    out = []
    for fg, bg, need in CONTRAST_GATES:
        ratio = p.roles[fg].contrast(p.roles[bg])
        if ratio < need:
            out.append(f"{fg} on {bg}: {ratio:.2f}:1, needs {need}:1")
    return out
