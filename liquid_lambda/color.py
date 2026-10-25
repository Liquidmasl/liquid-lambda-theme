"""sRGB colours built from OKLCH, with the gamut mapping, OKLab mixing and
WCAG contrast the palette needs.

The OKLCH -> sRGB path is mirrored line for line in templates/tuner/engine.js;
tests/test_parity.py keeps the two in step.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def _js_round(x: float) -> int:
    # Math.round, not Python's round-half-to-even, so hex values match the tuner
    return math.floor(x + 0.5)


def _encode(x: float) -> float:
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def _decode(x: float) -> float:
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def _oklab_to_linear(L: float, a: float, b: float) -> tuple[float, float, float]:
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1 / 3), x)


def _linear_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    l = _cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = _cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = _cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _oklch_to_linear(L: float, C: float, h: float) -> tuple[float, float, float]:
    rad = h * math.pi / 180
    return _oklab_to_linear(L, C * math.cos(rad), C * math.sin(rad))


def _in_gamut(rgb: tuple[float, float, float]) -> bool:
    return all(-1e-4 <= v <= 1 + 1e-4 for v in rgb)


@dataclass(frozen=True)
class Color:
    """An sRGB colour, stored as its 8-bit channels so what is checked is what ships."""

    r: int
    g: int
    b: int

    @classmethod
    def oklch(cls, L: float, C: float, h: float) -> Color:
        """Colour at lightness L, chroma C, hue h; chroma is reduced until it fits sRGB."""
        rgb = _oklch_to_linear(L, C, h)
        if not _in_gamut(rgb):
            lo, hi = 0.0, C
            for _ in range(24):
                mid = (lo + hi) / 2
                if _in_gamut(_oklch_to_linear(L, mid, h)):
                    lo = mid
                else:
                    hi = mid
            rgb = _oklch_to_linear(L, lo, h)
        return cls._from_linear(rgb)

    @classmethod
    def hex(cls, value: str) -> Color:
        v = value.strip().lstrip("#")
        if len(v) != 6 or any(c not in "0123456789abcdefABCDEF" for c in v):
            raise ValueError(f"not a #RRGGBB colour: {value!r}")
        return cls(int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))

    @classmethod
    def _from_linear(cls, rgb: tuple[float, float, float]) -> Color:
        r, g, b = (_js_round(_encode(min(1.0, max(0.0, v))) * 255) for v in rgb)
        return cls(r, g, b)

    def _linear(self) -> tuple[float, float, float]:
        return tuple(_decode(c / 255) for c in (self.r, self.g, self.b))  # type: ignore[return-value]

    # formats for templates
    @property
    def hex_str(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def strip(self) -> str:
        return self.hex_str[1:]

    @property
    def rgb(self) -> str:
        return f"{self.r}, {self.g}, {self.b}"

    def rgba(self, alpha: float) -> str:
        return f"rgba({self.r}, {self.g}, {self.b}, {alpha})"

    @property
    def ansi_fg(self) -> str:
        """SGR parameters for this colour as a truecolor foreground, e.g. 38;2;79;220;246."""
        return f"38;2;{self.r};{self.g};{self.b}"

    def __str__(self) -> str:
        return self.hex_str

    def mix(self, other: Color, t: float) -> Color:
        """Blend toward other by t (0 = self, 1 = other) in OKLab, like CSS color-mix(in oklab)."""
        a = _linear_to_oklab(*self._linear())
        b = _linear_to_oklab(*other._linear())
        return Color._from_linear(_oklab_to_linear(*(x + (y - x) * t for x, y in zip(a, b))))

    @property
    def luminance(self) -> float:
        r, g, b = self._linear()
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast(self, other: Color) -> float:
        hi, lo = sorted((self.luminance, other.luminance), reverse=True)
        return (hi + 0.05) / (lo + 0.05)
