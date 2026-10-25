"""Generated binary assets: things a text template cannot produce.

Each generator writes its outputs under a staging root that mirrors the repo;
`build` moves changed outputs into place, `check` compares them byte for byte.
"""

from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from .palette import Palette

CURSOR = "cursors/Oxygen-Lambda-Lead"
CURSOR_PREVIEW = "assets/cursors/Oxygen-Lambda-Lead.png"


def cursors(root: Path, stage: Path, p: Palette) -> None:
    """The Oxygen cursor in the lead colour, from the uncoloured base theme."""
    (stage / CURSOR_PREVIEW).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-I", str(root / "cursors/recolour.py"),
         "--base", str(root / "cursors/base"), "--out", str(stage / CURSOR),
         "--name", "Oxygen Lambda Lead", "--colour", p.lead.hex_str, "--spread", "0.11",
         "--preview", str(stage / CURSOR_PREVIEW), "--bg", p.bg.hex_str],
        check=True, capture_output=True,
    )


GENERATORS: tuple[tuple[tuple[str, ...], Callable[[Path, Path, Palette], None]], ...] = (
    ((CURSOR, CURSOR_PREVIEW), cursors),
)


def _same(a: Path, b: Path) -> bool:
    if a.is_dir() != b.is_dir() or not b.exists():
        return False
    if a.is_file():
        return filecmp.cmp(a, b, shallow=False)
    cmp = filecmp.dircmp(a, b)

    def clean(d: filecmp.dircmp) -> bool:
        if d.left_only or d.right_only or d.funny_files:
            return False
        _, mismatch, errors = filecmp.cmpfiles(d.left, d.right, d.common_files, shallow=False)
        return not mismatch and not errors and all(clean(s) for s in d.subdirs.values())

    return clean(cmp)


def stale(root: Path, p: Palette) -> list[str]:
    """Outputs whose committed copy differs from a fresh generation."""
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        for paths, gen in GENERATORS:
            gen(root, stage, p)
            out += [rel for rel in paths if not _same(stage / rel, root / rel)]
    return out


def build(root: Path, p: Palette) -> list[str]:
    """Regenerate every output, replacing the ones that changed; returns those."""
    changed = []
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        for paths, gen in GENERATORS:
            gen(root, stage, p)
            for rel in paths:
                new, old = stage / rel, root / rel
                if _same(new, old):
                    continue
                if old.is_dir() and not old.is_symlink():
                    shutil.rmtree(old)
                elif old.exists() or old.is_symlink():
                    old.unlink()
                old.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(new), str(old))
                changed.append(rel)
    return changed
