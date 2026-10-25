import pytest

from liquid_lambda.color import Color


def test_oklch_primaries():
    assert Color.oklch(0.627955, 0.257683, 29.2339).hex_str == "#ff0000"
    assert Color.oklch(1.0, 0.0, 0.0).hex_str == "#ffffff"
    assert Color.oklch(0.0, 0.0, 0.0).hex_str == "#000000"


def test_out_of_gamut_chroma_is_reduced_not_clipped_per_channel():
    c = Color.oklch(0.83, 0.4, 212)  # far outside sRGB
    assert all(0 <= v <= 255 for v in (c.r, c.g, c.b))
    # hue survives: still a cyan, blue and green both well above red
    assert c.b > c.r and c.g > c.r


def test_hex_parsing_and_formats():
    c = Color.hex("#4FDCF6")
    assert c.hex_str == "#4fdcf6"
    assert c.strip == "4fdcf6"
    assert c.rgb == "79, 220, 246"
    assert c.rgba(0.5) == "rgba(79, 220, 246, 0.5)"
    assert c.ansi_fg == "38;2;79;220;246"
    assert str(c) == "#4fdcf6"
    assert Color.hex("4fdcf6") == c
    with pytest.raises(ValueError):
        Color.hex("#12345")


def test_mix_endpoints_and_midpoint():
    a, b = Color.hex("#000000"), Color.hex("#ffffff")
    assert a.mix(b, 0) == a
    assert a.mix(b, 1) == b
    mid = a.mix(b, 0.5)
    assert mid.r == mid.g == mid.b and 90 < mid.r < 140  # OKLab midpoint, not sRGB 128 exactly


def test_contrast():
    assert Color.hex("#000000").contrast(Color.hex("#ffffff")) == pytest.approx(21.0)
    assert Color.hex("#777777").contrast(Color.hex("#777777")) == pytest.approx(1.0)
