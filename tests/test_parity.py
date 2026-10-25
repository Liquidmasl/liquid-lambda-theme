"""The tuner's JS engine and the Python engine must build the same palette."""

import itertools
import json
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path

import pytest

from liquid_lambda.palette import Settings, build

NODE = shutil.which("node")


def grid():
    for lead, tint, strength, loud, cyan, amber, chroma in itertools.product(
        ["cyan", "amber"], ["warm", "neutral", "cool"], [0, 55, 100], [20, 70, 100],
        [180, 212, 235], [35, 66, 85], [40, 85, 100],
    ):
        yield Settings(lead=lead, tint=tint, tint_strength=strength, second_loudness=loud,
                       cyan_hue=cyan, amber_hue=amber, lead_chroma=chroma)
    yield Settings(pin={"lead": "#00FF88", "bg": "101010"})


def channels(hex_str):
    return [int(hex_str[i:i + 2], 16) for i in (1, 3, 5)]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_engine_matches_python():
    cases = list(grid())
    out = subprocess.run(
        [NODE, str(Path(__file__).with_name("parity.mjs"))],
        input=json.dumps([asdict(s) for s in cases]), capture_output=True, text=True, check=True,
    )
    for s, js in zip(cases, json.loads(out.stdout), strict=True):
        py = build(s)
        assert set(js["roles"]) == set(py.roles), s
        pairs = [(js["roles"][k], py.roles[k].hex_str, k) for k in py.roles]
        pairs += [(j, p.hex_str, f"ansi{i}") for i, (j, p) in enumerate(zip(js["ansi"], py.ansi, strict=True))]
        for j, p, name in pairs:
            # libm and V8 may differ in the last bit of cos/sin: allow one step per channel
            assert all(abs(a - b) <= 1 for a, b in zip(channels(j), channels(p))), (name, j, p, s)
