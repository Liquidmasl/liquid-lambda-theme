# Firefox - Noir

Firefox chrome matching the COSMIC Noir rice. Same layout as the
Monochrome and DarkGold stylesheets, recoloured for charcoal and orange.

## Palette

| Hex       | Role                      |
|-----------|---------------------------|
| `#171717` | Frame, page chrome        |
| `#222222` | Panels, menus             |
| `#2A2A2A` | Hover row                 |
| `#3A3B3A` | Pressed row, separators, menu border |
| `#7D837D` | Muted text                |
| `#F25623` | Accent, URL bar border    |
| `#88A57D` | Secondary accent, active  |
| `#959C95` | Links                     |
| `#CCD0CF` | Body text, hover text     |

## Structure

```
firefox/
├── chrome/
│   ├── userChrome.css    browser UI: rounded corners, solid menu hover
│   └── userContent.css   new tab page: accent colour only
└── install.sh            copies chrome/ into the default profile
```

No WebExtension theme package in this repo. Use Firefox's built-in **Dark**
theme plus these stylesheets. If you want the toolbar itself in the palette,
build a theme at [Firefox Color](https://color.firefox.com/) from the
palette above; it installs as an add-on without any coding.

## Setup

```bash
./install.sh
```

Copies `chrome/` into your `*.default-release` profile, backs up anything it
replaces, and adds the required pref to `user.js`. Then **fully restart**
Firefox - `userChrome.css` is parsed only at startup.

Manual equivalent:

1. `about:config` → `toolkit.legacyUserProfileCustomizations.stylesheets` = `true`
2. `about:support` → Profile Directory → Open Directory
3. Copy `chrome/` in
4. Restart

To undo: delete the two files from the profile's `chrome/` folder and restart.

## Notes

- **Never set `--panel-*` or `--arrowpanel-*` on `:root`.** Those variables leak
  into the toolbar and blank the URL bar. They stay on the popup elements.
- **Context menus do not get an extra element border.** A second stroke made
  the right-click panel look detached. Hover is a solid `#2A2A2A` row, not an
  inset ring.
- **`[_moz-menuactive="true"]` is required.** Firefox marks the active
  context-menu row with that attribute, not only `:hover`.
- **`userContent.css` sets colour variables only.** No size or position rules
  on new-tab tiles.
- Built against **Firefox 154**.

## License

MIT, same as the rest of the repo.
