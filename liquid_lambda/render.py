"""Render templates/<path>.j2 to <path> in the repo, from one palette.

Templates see every role as a variable ({{ lead }} prints #rrggbb) with the
formats on Color ({{ lead.strip }}, {{ bg.rgba(0.8) }}, {{ lead.mix(bg, 0.2) }}),
plus `ansi` (the 16 terminal colours), `settings` (the palette.toml inputs)
and `contrast_gates`.
Files without .j2 in templates/ are only there to be included.
"""

from __future__ import annotations

import base64
import mimetypes
from dataclasses import asdict
from pathlib import Path

import jinja2

from .palette import CONTRAST_GATES, Palette, Settings

SUFFIX = ".j2"


def environment(templates: Path) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


def context(palette: Palette, settings: Settings, **extra: object) -> dict[str, object]:
    return {
        **palette.roles,
        "ansi": palette.ansi,
        "settings": asdict(settings),
        "contrast_gates": CONTRAST_GATES,
        "wallpaper": None,
        **extra,
    }


def template_names(templates: Path) -> list[str]:
    return sorted(p.relative_to(templates).as_posix() for p in templates.rglob(f"*{SUFFIX}"))


def render_all(root: Path, palette: Palette, settings: Settings) -> dict[Path, str]:
    """Every generated file, keyed by its path under root."""
    templates = root / "templates"
    env = environment(templates)
    ctx = context(palette, settings)
    return {root / name.removesuffix(SUFFIX): env.get_template(name).render(ctx) for name in template_names(templates)}


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def render_preview(root: Path, palette: Palette, settings: Settings, wallpaper: Path | None) -> str:
    env = environment(root / "templates")
    ctx = context(palette, settings, wallpaper=data_uri(wallpaper) if wallpaper else None)
    return env.get_template(f"tuner/index.html{SUFFIX}").render(ctx)
