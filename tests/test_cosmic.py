import pytest

from liquid_lambda.cosmic import current_wallpaper


@pytest.fixture
def cosmic(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    d = tmp_path / "cosmic/com.system76.CosmicBackground/v1"
    d.mkdir(parents=True)

    def entry(name, source):
        (d / name).write_text(f'(\n    output: "x",\n    source: {source},\n    scaling_mode: Zoom,\n)\n')

    return d, entry


def test_same_on_all_uses_the_all_entry(cosmic, tmp_path):
    d, entry = cosmic
    (d / "same-on-all").write_text("true")
    entry("all", f'Path("{tmp_path}/one.png")')
    assert current_wallpaper() == tmp_path / "one.png"


def test_per_screen_takes_the_most_common_image(cosmic, tmp_path):
    d, entry = cosmic
    (d / "same-on-all").write_text("false")
    (d / "backgrounds").write_text('[\n    "DP-3",\n    "DP-1",\n    "DP-2",\n]')
    entry("output.DP-3", f'Path("{tmp_path}/left screen.png")')
    entry("output.DP-1", f'Path("{tmp_path}/wide.png")')
    entry("output.DP-2", f'Path("{tmp_path}/wide.png")')
    assert current_wallpaper() == tmp_path / "wide.png"
    assert current_wallpaper("DP-3") == tmp_path / "left screen.png"
    with pytest.raises(ValueError, match="DP-9"):
        current_wallpaper("DP-9")


def test_slideshow_folder_takes_the_first_image(cosmic, tmp_path):
    d, entry = cosmic
    shows = tmp_path / "shows"
    shows.mkdir()
    for n in ("b.jpg", "a.png", "notes.txt"):
        (shows / n).write_bytes(b"")
    (d / "same-on-all").write_text("true")
    entry("all", f'Path("{shows}")')
    assert current_wallpaper() == shows / "a.png"


def test_colour_background_is_reported(cosmic):
    d, entry = cosmic
    (d / "same-on-all").write_text("true")
    entry("all", "Color(Single((0.1, 0.1, 0.1)))")
    with pytest.raises(ValueError, match="colour or gradient"):
        current_wallpaper()
