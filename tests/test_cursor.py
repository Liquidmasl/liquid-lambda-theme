import struct

import pytest

from liquid_lambda import cursor
from liquid_lambda.cli import ROOT
from liquid_lambda.palette import DEFAULT_CURSOR, Settings, build


def test_xcursor_layout():
    frames = [cursor.Frame(s, bytes(4 * s * s), 1, 2, d) for s, d in ((24, 0), (32, 30))]
    data = cursor.xcursor(frames)
    magic, header, _, ntoc = struct.unpack_from("<4sIII", data)
    assert (magic, header, ntoc) == (b"Xcur", 16, 2)
    for i, f in enumerate(frames):
        typ, size, pos = struct.unpack_from("<III", data, 16 + 12 * i)
        assert (typ, size) == (0xFFFD0002, f.size)
        _, _, sub, _, w, h, xh, yh, delay = struct.unpack_from("<IIIIIIIII", data, pos)
        assert (sub, w, h, xh, yh, delay) == (f.size, f.size, f.size, 1, 2, f.delay)
    assert len(data) == 16 + 12 * 2 + sum(36 + 4 * f.size ** 2 for f in frames)


@pytest.mark.parametrize("recipe", [{"base": "bibata"}, {"pointer": "nope"}, {"wait": "compose"}])
def test_recipe_is_checked_before_fetching(recipe):
    with pytest.raises(ValueError, match=r"\[cursor\]"):
        cursor.validate(recipe)


def test_palette_toml_cursor_section(tmp_path):
    f = tmp_path / "palette.toml"
    f.write_text('[palette]\nlead = "cyan"\n\n[cursor]\npointer = "bibata"\n')
    assert Settings.load(f).cursor == {**DEFAULT_CURSOR, "pointer": "bibata"}
    cursor.validate(Settings.load(ROOT / "palette.toml").cursor)


CACHED = all((cursor.cache_dir() / f"{n}-{s.commit[:12]}/.git").is_dir() for n, s in cursor.SOURCES.items())


@pytest.mark.skipif(not CACHED, reason="cursor sources not fetched yet (lambda apply --only cursors)")
def test_build_mixes_sources(tmp_path):
    mixed = cursor.build(build(Settings()), DEFAULT_CURSOR, tmp_path / "t")
    cur = tmp_path / "t/cursors"
    assert "default from bibata" in mixed and "progress composed from default + wait" in mixed
    assert (cur / "left_ptr").resolve() == (cur / "default").resolve()
    assert (cur / "pointer").is_file() and (cur / "hand2").is_symlink()
    wait = (cur / "wait").read_bytes()
    assert struct.unpack_from("<4sIII", wait)[3] == 40 * len(cursor.SIZES)  # animated, every size
