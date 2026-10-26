# Cursor

`lambda apply` builds **Lambda-Cursors** into `~/.local/share/icons/` from
vector cursor themes, recoloured to the palette and rendered at 24, 32, 48, 64
and 96 px, so it stays sharp at any scale (`liquid_lambda/cursor.py`).

| Role | Source (default recipe) | Look |
|------|-------------------------|------|
| everything else | [Capitaine](https://github.com/keeferrourke/capitaine-cursors) (LGPL-3.0) | lead body, background outline |
| `default` (the arrow) | [Bibata Original](https://github.com/ful1e5/Bibata_Cursor) (GPL-3.0), scaled to Capitaine's size | lead body, background outline |
| `wait` | [Simp1e](https://gitlab.com/cursors/simp1e) (GPL-3.0), 40 frames | dark body, lead ring, second-colour spinner |
| `progress` | composed: the arrow with the `wait` spinner | |

Badges and accents inside cursors (help, copy, not-allowed) move to the
palette colour of their hue family.

The sources are fetched at pinned commits into
`~/.cache/liquid-lambda/cursor-sources/` and never copied into this repo, so
their licences stay with them. Mix your own in `palette.toml`:

```toml
[cursor]
base = "capitaine"
default = "bibata"
pointer = "bibata"     # any role name Capitaine has, from any source that has it
wait = "simp1e"
progress = "compose"
```

## Install

```bash
uv run lambda apply --only cursors   # build into ~/.local/share/icons
./cursors/install.sh                 # activate (sudo), copies to /usr/share/icons too
reboot                               # or log out and back in
```

COSMIC has no cursor picker yet, so `install.sh` sets the cursor itself:

| Where | What |
|-------|------|
| `/etc/environment` | `XCURSOR_THEME` / `XCURSOR_SIZE`, read by cosmic-comp at login |
| `~/.icons/default/index.theme` | X11 / XWayland apps |
| gsettings | GTK apps |
| Flatpak override | Flatpak apps (they do not read `/etc/environment`) |

Options: `--user` (skip the `/usr/share/icons` copy), `--size N` (default 24).
Every file it changes gets a `.bak-<timestamp>` copy. `./cursors/uninstall.sh`
removes the theme and puts the Pop!_OS default back.
