import pytest

from liquid_lambda.palette import BASE_ROLES, Settings, build, contrast_failures


def test_defaults_pass_every_contrast_gate():
    assert contrast_failures(build(Settings())) == []


@pytest.mark.parametrize("lead", ["cyan", "amber"])
@pytest.mark.parametrize("tint", ["warm", "neutral", "cool"])
def test_both_leads_and_all_tints_pass(lead, tint):
    assert contrast_failures(build(Settings(lead=lead, tint=tint))) == []


def test_lead_swaps_the_aliases():
    b = build(Settings(lead="cyan"))
    assert b.cyan == b.lead and b.amber == b.second and b.warn == b.amber
    a = build(Settings(lead="amber"))
    assert a.amber == a.lead and a.cyan == a.second
    assert a.warn == a.yellow  # warnings leave the accent hue when amber leads


def test_ansi_has_16_slots_built_from_roles():
    p = build(Settings())
    assert len(p.ansi) == 16
    assert p.ansi[6] == p.cyan and p.ansi[3] == p.amber and p.ansi[15] == p.text


def test_pin_overrides_and_aliases_follow():
    p = build(Settings(pin={"lead": "#00ff88"}))
    assert p.lead.hex_str == "#00ff88"
    assert p.hint == p.lead and p.link == p.lead and p.ansi[6] == p.lead


def test_neutral_tint_is_grey():
    p = build(Settings(tint="neutral"))
    for role in ("bg", "surface2", "text"):
        c = p.roles[role]
        assert c.r == c.g == c.b


@pytest.mark.parametrize("bad", [
    {"lead": "teal"}, {"tint": "hot"}, {"tint_strength": 101}, {"second_loudness": 10},
    {"cyan_hue": 100}, {"amber_hue": 120}, {"lead_chroma": 20}, {"pin": {"nope": "#000000"}},
])
def test_rejects_bad_settings(bad):
    with pytest.raises(ValueError):
        Settings(**bad)


def test_load_rejects_unknown_keys(tmp_path):
    f = tmp_path / "palette.toml"
    f.write_text('[palette]\nlead = "cyan"\ncolour = 3\n')
    with pytest.raises(ValueError, match="colour"):
        Settings.load(f)


def test_every_pinnable_role_exists():
    p = build(Settings())
    assert set(BASE_ROLES) <= set(p.roles)
