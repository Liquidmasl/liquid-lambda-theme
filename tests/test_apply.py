import json
import tomllib

import pytest

from liquid_lambda.apply import Ctx, apply, with_block
from liquid_lambda.cli import ROOT


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    return tmp_path


def test_with_block_inserts_then_replaces():
    once = with_block("a = 1\n", "x", "b = 2")
    assert once == "a = 1\n\n# >>> liquid-lambda x >>>\nb = 2\n# <<< liquid-lambda x <<<\n"
    assert with_block(once, "x", "b = 3").count("liquid-lambda x >>>") == 1
    assert "b = 3" in with_block(once, "x", "b = 3")
    assert with_block("a = 1\n", "t", "p = 1", at_top=True).startswith("# >>> liquid-lambda t >>>\np = 1")


def test_wezterm_links_scheme_and_asks_for_color_scheme(home):
    todo = apply(Ctx(ROOT), ["wezterm"])
    dest = home / ".config/wezterm/colors/Lambda.toml"
    assert dest.is_symlink() and dest.resolve() == (ROOT / "wezterm/Lambda.toml").resolve()
    assert tomllib.loads(dest.read_text())["metadata"]["name"] == "Lambda"
    assert any("color_scheme = 'Lambda'" in t for t in todo)
    (home / ".config/wezterm/wezterm.lua").write_text("config.color_scheme = 'Lambda'\n")
    assert apply(Ctx(ROOT), ["wezterm"]) == []


def test_starship_keeps_user_config_and_is_idempotent(home):
    cfg = home / ".config/starship.toml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('add_newline = false\n\n[hostname]\nstyle = "bold green"\n')
    apply(Ctx(ROOT), ["starship"])
    data = tomllib.loads(cfg.read_text())
    assert data["palette"] == "lambda" and data["add_newline"] is False
    assert data["hostname"]["style"] == "bold green"
    assert data["palettes"]["lambda"]["cyan"].startswith("#")
    first = cfg.read_text()
    ctx = Ctx(ROOT)
    apply(ctx, ["starship"])
    assert cfg.read_text() == first and ctx.log == []
    assert list(cfg.parent.glob("starship.toml.bak-*"))


def test_starship_refuses_a_second_palette(home):
    cfg = home / ".config/starship.toml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('palette = "mine"\n')
    with pytest.raises(ValueError, match="already selects a palette"):
        apply(Ctx(ROOT), ["starship"])
    assert cfg.read_text() == 'palette = "mine"\n'


def test_prismantis_merges_colours_and_keeps_other_settings(home):
    path = home / ".claude/settings.json"
    path.parent.mkdir()
    path.write_text(json.dumps({"theme": "dark", "pluginConfigs": {"prismantis@prismantis": {"options": {"tableStyle": "box"}}}}))
    apply(Ctx(ROOT), ["prismantis"])
    data = json.loads(path.read_text())
    opts = data["pluginConfigs"]["prismantis@prismantis"]["options"]
    assert data["theme"] == "dark" and opts["tableStyle"] == "box"
    assert len([k for k in opts if k.endswith("Color")]) == 22


def test_dry_run_changes_nothing(home):
    ctx = Ctx(ROOT, dry_run=True)
    apply(ctx, ["wezterm", "starship"])
    assert ctx.log and not (home / ".config").exists()


def test_unknown_target():
    with pytest.raises(ValueError, match="unknown targets"):
        apply(Ctx(ROOT), ["emacs"])
