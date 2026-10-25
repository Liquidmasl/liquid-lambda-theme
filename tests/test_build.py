from liquid_lambda.cli import ROOT, main
from liquid_lambda.palette import Settings, build
from liquid_lambda.render import render_all, render_preview


def test_committed_files_are_up_to_date():
    assert main(["check"]) == 0


def test_committed_tuner_carries_no_wallpaper():
    s = Settings.load(ROOT / "palette.toml")
    tuner = render_all(ROOT, build(s), s)[ROOT / "tuner/index.html"]
    assert "data:image" not in tuner
    assert build(s).lead.hex_str in tuner


def test_preview_embeds_the_wallpaper(tmp_path):
    img = tmp_path / "w.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    s = Settings()
    assert "data:image/png;base64," in render_preview(ROOT, build(s), s, img)
