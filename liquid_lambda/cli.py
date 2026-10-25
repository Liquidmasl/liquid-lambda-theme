"""lambda build | check | preview"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from .cosmic import current_wallpaper
from .palette import Settings, build, contrast_failures
from .render import render_all, render_preview

ROOT = Path(__file__).resolve().parents[1]
LOCAL_PREVIEW = Path("tuner/local.html")  # gitignored: may carry a private wallpaper
COSMIC = object()  # --wallpaper given without a path


def _load(path: Path):
    settings = Settings.load(path)
    return settings, build(settings)


def cmd_build(args: argparse.Namespace) -> int:
    settings, palette = _load(args.palette)
    failures = contrast_failures(palette)
    for f in failures:
        print(f"contrast: {f}", file=sys.stderr)
    for path, text in render_all(ROOT, palette, settings).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text() != text:
            path.write_text(text)
            print(f"wrote {path.relative_to(ROOT)}")
    return 1 if failures else 0


def cmd_check(args: argparse.Namespace) -> int:
    settings, palette = _load(args.palette)
    problems = [f"contrast: {f}" for f in contrast_failures(palette)]
    for path, text in render_all(ROOT, palette, settings).items():
        if not path.exists() or path.read_text() != text:
            problems.append(f"stale: {path.relative_to(ROOT)} (run: uv run lambda build)")
    for p in problems:
        print(p, file=sys.stderr)
    if not problems:
        print("palette ok, generated files up to date")
    return 1 if problems else 0


def cmd_preview(args: argparse.Namespace) -> int:
    settings, palette = _load(args.palette)
    wallpaper = args.wallpaper
    if wallpaper is COSMIC or args.output:
        wallpaper = current_wallpaper(args.output)
        print(f"wallpaper: {wallpaper}")
    if wallpaper and not Path(wallpaper).is_file():
        raise ValueError(f"wallpaper not found: {wallpaper}")
    out = ROOT / LOCAL_PREVIEW
    out.write_text(render_preview(ROOT, palette, settings, Path(wallpaper) if wallpaper else None))
    print(out)
    if args.open:
        webbrowser.open(out.as_uri())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lambda", description="Liquid Lambda theme generator")
    parser.add_argument("--palette", type=Path, default=ROOT / "palette.toml", help="palette file (default: palette.toml)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="render every template from the palette").set_defaults(func=cmd_build)
    sub.add_parser("check", help="fail on contrast problems or out-of-date generated files").set_defaults(func=cmd_check)
    p = sub.add_parser("preview", help=f"write the tuner to {LOCAL_PREVIEW}, optionally on your wallpaper")
    p.add_argument("--wallpaper", nargs="?", const=COSMIC, metavar="PATH",
                   help="image behind the mock desktop, stays local; without PATH, the one COSMIC shows")
    p.add_argument("--output", metavar="NAME", help="with several wallpapers, take the one on this screen (e.g. DP-1)")
    p.add_argument("--no-open", dest="open", action="store_false", help="only write the file, do not open a browser")
    p.set_defaults(func=cmd_preview)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
