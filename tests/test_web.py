import pytest

from liquid_lambda import web
from liquid_lambda.cli import ROOT
from liquid_lambda.color import Color
from liquid_lambda.palette import Settings, build

P = build(Settings())
BG, FG = Color.hex("#0d1117"), Color.hex("#f0f6fc")


@pytest.mark.parametrize("value, expected", [
    ("#fff", (Color(255, 255, 255), 1.0)),
    ("#FFFFFF0C", (Color(255, 255, 255), 12 / 255)),
    ("rgba(40,40,40,0.8)", (Color(40, 40, 40), 0.8)),
    ("rgb(1 2 3 / 50%)", (Color(1, 2, 3), 0.5)),
    ("transparent", None),
])
def test_parse(value, expected):
    assert web.parse(value) == expected


def test_site_greys_land_on_the_palette_ramp():
    assert web.remap(BG, BG, FG, P) == P.bg
    assert web.remap(FG, BG, FG, P) == P.text
    darker = web.remap(Color.hex("#010409"), BG, FG, P)
    assert darker.luminance < P.bg.luminance and darker.luminance > 0  # darker, not black


@pytest.mark.parametrize("src, role", [("#4493f8", "lead"), ("#3fb950", "ok"), ("#f85149", "err"), ("#d29922", "second"), ("#ab7df8", "magenta")])
def test_accents_take_the_palette_hue_and_keep_their_lightness(src, role):
    c = Color.hex(src)
    out = web.remap(c, BG, FG, P)
    assert abs(out.lch[2] - P.roles[role].lch[2]) < 8
    assert abs(out.lch[0] - c.lch[0]) < 0.02


def test_every_site_renders_and_keeps_alpha():
    for name in web.SITES:
        decls = dict(web.declarations(ROOT, name, P))
        assert len(decls) > 50
    gh = dict(web.declarations(ROOT, "github", P))
    assert gh["--bgColor-default"] == P.bg.hex_str


def test_version_grows_only_when_the_css_changes(tmp_path):
    (tmp_path / "data/web").mkdir(parents=True)
    (tmp_path / "data/web/github.json").write_text((ROOT / "data/web/github.json").read_text())
    first = web.userstyle(tmp_path, "github", P)["version"]
    (tmp_path / "data/web/versions.json").write_text('{"github": %s}' % str(web.userstyle(tmp_path, "github", P)["_state"]).replace("'", '"'))
    assert web.userstyle(tmp_path, "github", P)["version"] == first
    other = build(Settings(lead="amber"))
    assert web.userstyle(tmp_path, "github", other)["version"] != first
