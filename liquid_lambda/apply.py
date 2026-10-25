"""`lambda apply`: put the generated files where each app reads them.

Each target is one function that installs from the built repo files and
returns the steps it could not do itself. Files the user owns (starship.toml,
Claude Code's settings.json) are edited in place: only a marked block or our
own keys change, after a timestamped backup. Whole files we generate are
symlinked, so a later `lambda build` updates them without another apply.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import time
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

STAMP = time.strftime("%Y%m%d-%H%M%S")


@dataclass
class Ctx:
    root: Path
    dry_run: bool = False
    log: list[str] = field(default_factory=list)

    @property
    def home(self) -> Path:
        return Path.home()

    @property
    def config(self) -> Path:
        return Path(os.environ.get("XDG_CONFIG_HOME") or self.home / ".config")

    def say(self, msg: str) -> None:
        self.log.append(("would " if self.dry_run else "") + msg)


def _backup(ctx: Ctx, path: Path) -> None:
    bak = path.with_name(f"{path.name}.bak-{STAMP}")
    if not ctx.dry_run:
        shutil.copy2(path, bak) if not path.is_symlink() else path.rename(bak)
    ctx.say(f"back up {path} -> {bak.name}")


def link(ctx: Ctx, src: Path, dest: Path) -> None:
    """Symlink dest to src, backing up whatever was there."""
    if dest.is_symlink() and dest.resolve() == src.resolve():
        return
    if dest.exists() or dest.is_symlink():
        _backup(ctx, dest)
        if not ctx.dry_run and dest.exists() and not dest.is_symlink():
            dest.unlink()
    if not ctx.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(src.resolve())
    ctx.say(f"link {dest} -> {src.relative_to(ctx.root)}")


def write(ctx: Ctx, path: Path, text: str) -> None:
    """Replace path's content with text if it differs, backing up the old file."""
    if path.exists() and path.read_text() == text:
        return
    if path.exists():
        _backup(ctx, path)
    if not ctx.dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    ctx.say(f"update {path}")


def with_block(text: str, name: str, body: str, at_top: bool = False) -> str:
    """text with the block between `# >>> liquid-lambda NAME` markers set to body."""
    start, end = f"# >>> liquid-lambda {name} >>>", f"# <<< liquid-lambda {name} <<<"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    pattern = re.compile(rf"^{re.escape(start)}\n.*?^{re.escape(end)}\n?", re.S | re.M)
    if pattern.search(text):
        return pattern.sub(lambda _: block, text, count=1)
    if at_top:
        return block + ("\n" + text if text else "")
    return (text.rstrip() + "\n\n" if text.strip() else "") + block


# targets ---------------------------------------------------------------


def wezterm(ctx: Ctx) -> list[str]:
    link(ctx, ctx.root / "wezterm/Lambda.toml", ctx.config / "wezterm/colors/Lambda.toml")
    lua = ctx.config / "wezterm/wezterm.lua"
    if lua.exists() and re.search(r"""^\s*config\.color_scheme\s*=\s*['"]Lambda['"]""", lua.read_text(), re.M):
        return []
    return [f"WezTerm: set  config.color_scheme = 'Lambda'  in {lua}"]


def starship(ctx: Ctx) -> list[str]:
    path = ctx.config / "starship.toml"
    text = path.read_text() if path.exists() else ""
    stripped = re.sub(r"^# >>> liquid-lambda .*?^# <<< liquid-lambda .*?\n", "", text, flags=re.S | re.M)
    if re.search(r"^\s*palette\s*=", stripped, re.M):
        raise ValueError(f"{path} already selects a palette; remove that `palette = ...` line and apply again")
    table = (ctx.root / "starship/palette.toml").read_text()
    new = with_block(text, "palette-select", 'palette = "lambda"', at_top=True)
    new = with_block(new, "palette", table)
    tomllib.loads(new)  # never write a config starship cannot parse
    write(ctx, path, new)
    return []


PRISMANTIS = "prismantis@prismantis"


def prismantis(ctx: Ctx) -> list[str]:
    path = ctx.home / ".claude/settings.json"
    if not path.exists():
        return [f"prismantis: no {path}; is Claude Code installed?"]
    settings = json.loads(path.read_text())
    colours = json.loads((ctx.root / "prismantis/lambda.json").read_text())
    options = settings.setdefault("pluginConfigs", {}).setdefault(PRISMANTIS, {}).setdefault("options", {})
    options.update(colours)
    write(ctx, path, json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
    return ["prismantis: run /reload in open Claude Code sessions"]


TARGETS: dict[str, Callable[[Ctx], list[str]]] = {
    "wezterm": wezterm,
    "starship": starship,
    "prismantis": prismantis,
}


def apply(ctx: Ctx, names: list[str]) -> list[str]:
    unknown = sorted(set(names) - set(TARGETS))
    if unknown:
        raise ValueError(f"unknown targets {unknown}; known: {', '.join(TARGETS)}")
    todo = []
    for name in names:
        todo += TARGETS[name](ctx)
    return todo
