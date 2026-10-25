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
import subprocess
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
    todo: list[str] = field(default_factory=list)

    @property
    def home(self) -> Path:
        return Path.home()

    @property
    def config(self) -> Path:
        return Path(os.environ.get("XDG_CONFIG_HOME") or self.home / ".config")

    def say(self, msg: str) -> None:
        self.log.append(("would " if self.dry_run else "") + msg)


def _chezmoi_check(ctx: Ctx, path: Path) -> None:
    """A dotfile manager would undo the edit on its next run; say how to keep it."""
    if shutil.which("chezmoi") and subprocess.run(
        ["chezmoi", "source-path", str(path)], capture_output=True
    ).returncode == 0:
        ctx.todo.append(f"chezmoi manages {path}: keep the change with  chezmoi re-add {path}")


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
    _chezmoi_check(ctx, path)


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
    if lua.exists() and re.search(r"""^\s*(?:config\.)?color_scheme\s*=\s*['"]Lambda['"]""", lua.read_text(), re.M):
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


def zsh(ctx: Ctx) -> list[str]:
    # ~/.zshrc.local when there is one: often the machine-local file a dotfile
    # manager leaves alone
    rc = ctx.home / ".zshrc.local"
    if not rc.exists():
        rc = ctx.home / ".zshrc"
    text = rc.read_text() if rc.exists() else ""
    line = f'source "{(ctx.root / "zsh/lambda.zsh").resolve()}"'
    write(ctx, rc, with_block(text, "zsh", line))
    return ["zsh: open a new shell (exec zsh)"]


def fastfetch(ctx: Ctx) -> list[str]:
    for name in ("config.jsonc", "cosmic.txt"):
        link(ctx, ctx.root / "fastfetch" / name, ctx.config / "fastfetch" / name)
    return []


def btop(ctx: Ctx) -> list[str]:
    link(ctx, ctx.root / "btop/Lambda.theme", ctx.config / "btop/themes/Lambda.theme")
    conf = ctx.config / "btop/btop.conf"
    if not conf.exists():
        return ["btop: start btop once, then apply again to select the theme (or pick Lambda in its options)"]
    text = conf.read_text()
    new, n = re.subn(r'^color_theme\s*=.*$', 'color_theme = "Lambda"', text, flags=re.M)
    write(ctx, conf, new if n else text.rstrip() + '\ncolor_theme = "Lambda"\n')
    return ["btop: quit running btop first, it rewrites btop.conf on exit"]


def cosmic(ctx: Ctx) -> list[str]:
    # COSMIC apps read a theme libcosmic computes from these builder values;
    # there is no CLI to import one, so this stays a Settings step for now
    ron = (ctx.root / "cosmic/Lambda.ron").resolve()
    return [f"COSMIC: Settings -> Desktop -> Appearance -> Dark -> Import  {ron}"]


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
    "zsh": zsh,
    "fastfetch": fastfetch,
    "btop": btop,
    "cosmic": cosmic,
}


def apply(ctx: Ctx, names: list[str]) -> list[str]:
    unknown = sorted(set(names) - set(TARGETS))
    if unknown:
        raise ValueError(f"unknown targets {unknown}; known: {', '.join(TARGETS)}")
    todo = []
    for name in names:
        todo += TARGETS[name](ctx)
    return ctx.todo + todo
