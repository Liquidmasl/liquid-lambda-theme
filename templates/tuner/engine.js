// Palette engine for the tuner: a line-for-line mirror of liquid_lambda/color.py
// (Color.oklch) and liquid_lambda/palette.py (build). Change both together;
// tests/test_parity.py runs this file under node and compares the output.
(function (root) {
  "use strict";

  const TINT_HUE = { warm: 28, neutral: 0 };
  const MAX_TINT_CHROMA = 0.028;
  const CYAN = [0.83, 0.145];
  const AMBER = [0.74, 0.155];
  const NEUTRALS = {
    bg: [0.165, 1], surface1: [0.2, 1], surface2: [0.24, 1], surface3: [0.29, 1], line: [0.37, 0.9],
    dim: [0.54, 0.7], muted: [0.64, 0.6], sub: [0.78, 0.45], text: [0.91, 0.3],
  };

  const encode = x => x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
  const decode = x => x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);

  function oklchToLinear(L, C, h) {
    const rad = h * Math.PI / 180, a = C * Math.cos(rad), b = C * Math.sin(rad);
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
    const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
    const s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3;
    return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s];
  }
  const inGamut = rgb => rgb.every(v => v >= -1e-4 && v <= 1 + 1e-4);

  function fromLinear(rgb) {
    return "#" + rgb.map(v => Math.round(encode(Math.min(1, Math.max(0, v))) * 255).toString(16).padStart(2, "0")).join("");
  }

  function oklch(L, C, h) {
    let rgb = oklchToLinear(L, C, h);
    if (!inGamut(rgb)) {
      let lo = 0, hi = C;
      for (let i = 0; i < 24; i++) {
        const mid = (lo + hi) / 2;
        if (inGamut(oklchToLinear(L, mid, h))) lo = mid; else hi = mid;
      }
      rgb = oklchToLinear(L, lo, h);
    }
    return fromLinear(rgb);
  }

  function luminance(hex) {
    const [r, g, b] = [1, 3, 5].map(i => decode(parseInt(hex.slice(i, i + 2), 16) / 255));
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
  function contrast(a, b) {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  }

  // s: the [palette] keys of palette.toml plus pin; returns {roles: {name: "#rrggbb"}, ansi: [16]}
  function buildPalette(s) {
    const tintHue = s.tint === "cool" ? s.cyan_hue : TINT_HUE[s.tint];
    const tintChroma = s.tint === "neutral" ? 0 : s.tint_strength / 100 * MAX_TINT_CHROMA;
    const grey = (L, share = 1) => oklch(L, tintChroma * share, tintHue);

    const cyanFull = [...CYAN, s.cyan_hue], amberFull = [...AMBER, s.amber_hue];
    const [leadV, secondV] = s.lead === "cyan" ? [cyanFull, amberFull] : [amberFull, cyanFull];
    const leadK = s.lead_chroma / 100, secondK = s.second_loudness / 100;

    const r = {};
    for (const [role, [L, share]] of Object.entries(NEUTRALS)) r[role] = grey(L, share);
    Object.assign(r, {
      lead: oklch(leadV[0], leadV[1] * leadK, leadV[2]),
      second: oklch(secondV[0] - (1 - secondK) * 0.08, secondV[1] * secondK, secondV[2]),
      lead_ink: grey(0.17),
      second_ink: grey(0.17),
      ok: oklch(0.78, 0.1, 150),
      err: oklch(0.68, 0.17, 25),
      yellow: oklch(0.86, 0.13, 98),
      blue: oklch(0.72, 0.1, 255),
      magenta: oklch(0.72, 0.1, 330),
      err_bright: oklch(0.76, 0.16, 25),
      ok_bright: oklch(0.85, 0.1, 150),
      amber_bright: oklch(0.82, 0.14, s.amber_hue),
      blue_bright: oklch(0.8, 0.09, 255),
      magenta_bright: oklch(0.8, 0.09, 330),
      cyan_bright: oklch(0.9, 0.11, s.cyan_hue),
    });
    for (const [role, hex] of Object.entries(s.pin || {})) r[role] = "#" + hex.trim().replace(/^#/, "").toLowerCase();

    [r.cyan, r.amber] = s.lead === "cyan" ? [r.lead, r.second] : [r.second, r.lead];
    r.warn = s.lead === "cyan" ? r.amber : r.yellow;
    r.link = r.cyan;
    r.hint = r.lead;

    const ansi = [r.surface2, r.err, r.ok, r.amber, r.blue, r.magenta, r.cyan, r.sub,
                  r.dim, r.err_bright, r.ok_bright, r.amber_bright,
                  r.blue_bright, r.magenta_bright, r.cyan_bright, r.text];
    return { roles: r, ansi };
  }

  root.LambdaEngine = { buildPalette, contrast };
})(typeof globalThis !== "undefined" ? globalThis : this);
