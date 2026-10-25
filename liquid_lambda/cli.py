"""lambda build | check | preview | apply"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from . import assets
from .apply import TARGETS, Ctx, apply
from .cosmic import current_wallpaper
from .palette import Settings, build, contrast_failures
from .render import render_all, render_preview

ROOT = Path(__file__).resolve().parents[1]
LOCAL_PREVIEW = Path("tuner/local.html")  # gitignored: may carry a private wallpaper
COSMIC = object()  # --wallpaper given without a path


def _load(path: Path):
    settings = Settings.load(path)
    return settings, build(settings)


def _build(path: Path) -> bool:
    """Render everything; False when the palette fails a contrast gate."""
    settings, palette = _load(path)
    failures = contrast_failures(palette)
    for f in failures:
        print(f"contrast: {f}", file=sys.stderr)
    for out, text in render_all(ROOT, palette, settings).items():
        out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists() or out.read_text() != text:
            out.write_text(text)
            print(f"wrote {out.relative_to(ROOT)}")
    for rel in assets.build(ROOT, palette):
        print(f"wrote {rel}")
    return not failures


def cmd_build(args: argparse.Namespace) -> int:
    return 0 if _build(args.palette) else 1


def cmd_apply(args: argparse.Namespace) -> int:
    if args.list:
        print("\n".join(TARGETS))
        return 0
    if not _build(args.palette):
        print("not applying a palette that fails contrast; fix palette.toml first", file=sys.stderr)
        return 1
    names = args.only.split(",") if args.only else list(TARGETS)
    ctx = Ctx(root=ROOT, palette=_load(args.palette)[1], dry_run=args.dry_run)
    todo = apply(ctx, names)
    print("\n".join(ctx.log) or "already applied")
    if todo:
        print("\nleft to do by hand:\n" + "\n".join(f"  - {t}" for t in todo))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    settings, palette = _load(args.palette)
    problems = [f"contrast: {f}" for f in contrast_failures(palette)]
    for path, text in render_all(ROOT, palette, settings).items():
        if not path.exists() or path.read_text() != text:
            problems.append(f"stale: {path.relative_to(ROOT)} (run: uv run lambda build)")
    problems += [f"stale: {rel} (run: uv run lambda build)" for rel in assets.stale(ROOT, palette)]
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
    a = sub.add_parser("apply", help="build, then install the themes where each app reads them")
    a.add_argument("--only", metavar="A,B", help=f"comma-separated targets (default: all of {', '.join(TARGETS)})")
    a.add_argument("--dry-run", action="store_true", help="print what would change, change nothing")
    a.add_argument("--list", action="store_true", help="list the targets")
    a.set_defaults(func=cmd_apply)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
