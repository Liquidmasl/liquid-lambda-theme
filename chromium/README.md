# Chromium - Lambda

A Chromium theme generated from `palette.toml`
(`templates/chromium/theme/manifest.json.j2`). Brave, Chrome, Chromium and Edge all take it. No Chrome Web Store
and no Google account: it is loaded straight from this folder.

## Install

1. `chrome://extensions` (or `brave://extensions`) → turn on **Developer mode** (top right)
2. **Load unpacked** → pick `chromium/theme`

It applies at once and survives restarts. The browser keeps reading the folder, so
leave the clone where it is; after `lambda build`, press the reload arrow on the
theme's card.

To undo: `brave://settings/appearance` → Theme → **Reset to default**.

A theme replaces GTK / Classic mode in Appearance, and picking GTK or Classic
removes the theme.

### Packed instead

```bash
brave-browser --pack-extension="$PWD/chromium/theme"   # or google-chrome
```

That writes `chromium/theme.crx` and `chromium/theme.pem` next to the folder (both
are git-ignored). On Linux you can drag the `.crx` onto `brave://extensions`.
The `.pem` is the signing key for later versions, keep it private. Windows and
macOS refuse `.crx` files from outside the store, so use Load unpacked there.

## Palette

| Role | Where in the theme |
|------|--------------------|
| `bg` | Frame, inactive tabs, new tab page (incognito too) |
| `surface1` | Toolbar and active tab |
| `surface2` | Address bar |
| `text` / `sub` | Address bar and new tab text / bookmark bar text |
| `sub` toward `lead` | Toolbar icons |
| `muted` | Inactive tab text |
| `lead` | Active tab text, new tab links |

Chromium themes take `[R, G, B]` lists, not hex, so the template uses
`{{ role.rgb }}`.

## Notes

- **Colours only.** A Chromium theme has no keys for menus, the focus ring,
  the address bar dropdown or text selection; Chromium works those out from
  the frame and toolbar colours. There is no `userChrome.css` equivalent.
- **Brave's own panels** (Shields, sidebar, wallet, settings) follow Brave's
  dark mode, not the theme. Set `brave://settings/appearance` → Brave colors
  → **Dark**.
- **Brave's new tab page** is Brave's own and may ignore `ntp_background`.
  Pick a background on the page itself: **Customize** → Background image.
- **Web pages** are not themed. That is `brave://flags/#enable-force-dark`
  or a Dark Reader style extension.
- Built against **Brave 1.98 (Chromium 155)**.

## License

MIT, same as the rest of the repo.
