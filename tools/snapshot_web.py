"""Snapshot the colour custom properties a site defines in its dark theme.

    uv run --with playwright python tools/snapshot_web.py github reddit youtube google

Writes data/web/<site>.json ({"--var": "colour"}), the input of the web
userstyles. Re-run when a site changes its design tokens; the userstyles are
then rebuilt from the new snapshot by `lambda build`.
"""

import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITES = {
    "github": "https://github.com/Liquidmasl/liquid-lambda-theme",
    "reddit": "https://www.reddit.com/r/unixporn/",
    "youtube": "https://www.youtube.com/",
    "google": "https://www.google.com/search?q=cosmic+desktop&hl=en",
}
COLOUR = re.compile(r"^\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))\s*$")

# every custom property on the root element, computed, so theme selectors resolve
COLLECT = """() => {
  const out = {};
  const cs = getComputedStyle(document.documentElement);
  for (let i = 0; i < cs.length; i++) {
    const n = cs[i];
    if (n.startsWith('--')) out[n] = cs.getPropertyValue(n).trim();
  }
  return out;
}"""


def consent(page):
    # EU cookie walls (YouTube/Google, Reddit): decline and continue
    for label in ("Reject all", "Alle ablehnen", "Reject optional cookies"):
        btn = page.get_by_role("button", name=label)
        if btn.count():
            btn.first.click()
            page.wait_for_timeout(2500)
            return


def main(names):
    out_dir = ROOT / "data/web"
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(color_scheme="dark", locale="en-US", viewport={"width": 1400, "height": 900},
                                  user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
        for name in names:
            page = ctx.new_page()
            page.goto(SITES[name], wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)
            consent(page)
            props = page.evaluate(COLLECT)
            colours = {k: v for k, v in sorted(props.items()) if COLOUR.match(v)}
            (out_dir / f"{name}.json").write_text(json.dumps(colours, indent=1) + "\n")
            print(f"{name}: {len(colours)} colour properties of {len(props)} ({page.url})")
            page.close()
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:] or list(SITES))
