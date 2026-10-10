<div align="center">

# Pop!_OS · COSMIC · Noir

Pop!_OS 24.04 on COSMIC in charcoal, sage and orange: desktop, terminal,
shell, Firefox, cursor, wallpapers. The dark half of a pair; the light half is
[cosmic-dossier-theme](https://github.com/atraxsrc/cosmic-dossier-theme).

![Pop!_OS](https://img.shields.io/badge/Pop!_OS-24.04_LTS-f25623?style=for-the-badge&logo=popos&logoColor=white)
![COSMIC](https://img.shields.io/badge/COSMIC-1.0.0-88a57d?style=for-the-badge)
![Noir](https://img.shields.io/badge/Theme-Noir-171717?style=for-the-badge&labelColor=f25623)
![Firefox](https://img.shields.io/badge/Firefox-Noir-f56e0f?style=for-the-badge&logo=firefox-browser&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-7d837d?style=for-the-badge)

</div>

---

## Palette

From the Omarchy [Greek Noir](https://github.com/HANCORE-linux/omarchy-greek-noir-theme)
theme: a near-black base, grey-sage neutrals, one loud orange. The accent is
kept as is. Every text colour is at least 4.5:1 on the window background.

| Role | Color | Hex |
|------|-------|-----|
| Background | ![#171717](https://placehold.co/12x12/171717/171717.png) Charcoal | `#171717` |
| Containers | ![#222222](https://placehold.co/12x12/222222/222222.png) Soot / Slate | `#222222` / `#2A2A2A` |
| Text | ![#ccd0cf](https://placehold.co/12x12/ccd0cf/ccd0cf.png) Fog | `#CCD0CF` |
| Accent | ![#f25623](https://placehold.co/12x12/f25623/f25623.png) Orange | `#F25623` |
| Warning | ![#f56e0f](https://placehold.co/12x12/f56e0f/f56e0f.png) Ember | `#F56E0F` |
| Success | ![#88a57d](https://placehold.co/12x12/88a57d/88a57d.png) Sage | `#88A57D` |
| Khaki | ![#aeab94](https://placehold.co/12x12/aeab94/aeab94.png) Symlinks, yellow slot | `#AEAB94` |
| Grey-sage | ![#959c95](https://placehold.co/12x12/959c95/959c95.png) Directories | `#959C95` |
| Muted | ![#7d837d](https://placehold.co/12x12/7d837d/7d837d.png) Secondary text | `#7D837D` |
| Dim | ![#686c69](https://placehold.co/12x12/686c69/686c69.png) Comments | `#686C69` |
| Lines | ![#525252](https://placehold.co/12x12/525252/525252.png) Box lines, inactive | `#525252` |

Error shares the orange: the upstream palette has no red, and its "red" slot
is khaki. Errors are told apart by bold and underline.

| Role | Noir | Dossier |
|------|------|---------|
| Background | `#171717` | `#D0D0C8` |
| Text | `#CCD0CF` | `#242424` |
| Accent | `#F25623` | `#953B19` |
| Success | `#88A57D` | `#51573B` |

---

## Repo Structure

```
.
├── btop
│   └── Noir.theme               # btop colour theme
├── cosmic
│   ├── Noir.ron                 # COSMIC Appearance import (Dark)
│   ├── config/                  # baseline settings: fonts, icons, terminal look
│   └── install.sh
├── cosmic-term
│   └── Noir-term.ron            # COSMIC Terminal colour scheme
├── cursors
│   ├── Oxygen-02-Vibrant-Orange/ # cursor theme, patched for COSMIC apps
│   ├── install.sh
│   ├── uninstall.sh
│   └── README.md
├── fastfetch
│   ├── config.jsonc             # orange / grey-sage fastfetch config
│   ├── cosmic.txt               # COSMIC logo
│   └── install.sh
├── firefox
│   ├── chrome
│   │   ├── userChrome.css       # rounded chrome, soot menus
│   │   └── userContent.css      # new tab accent
│   ├── install.sh
│   └── README.md
├── lsd
│   ├── config.yaml              # theme: custom
│   ├── colors.yaml              # permission / size / date / git columns
│   └── install.sh
├── scripts
│   └── update_system.sh         # nala + flatpak, orange / sage ANSI
├── zsh
│   ├── noir.zsh                 # LS_COLORS, highlighting colours, aliases, starship
│   └── install.sh
├── assets/cursors               # cursor preview
├── LICENSE
└── README.md
```

---

## COSMIC Desktop

Settings → Desktop → Appearance → **Dark** → **Import** → `cosmic/Noir.ron`

Accent is orange `#F25623`. Use the `+` control if you want a custom swatch.

Frosted glass is on in the `.ron` at `frosted: VeryLow` for windows, panel,
applets and system UI (maximized apps stay solid), and corners are squared
(`radius_*: 2.0`), the same as the DarkGold baseline. Adjust frosted glass on
Appearance → Style → Frosted glass after import; those sliders survive a theme switch.

Export from Appearance if you tweak backgrounds / tints so you do not lose them.

Pairing tip: import `Dossier.ron` from
[cosmic-dossier-theme](https://github.com/atraxsrc/cosmic-dossier-theme) into
the Light slot and COSMIC's Dark / Light toggle flips between the two.
Wallpaper, Firefox and the shell layer do not follow the toggle; those are
per-rice files.

### Baseline settings

`cosmic/config/` holds the settings that make up the look and rarely change
(panel, dock, applets and shortcuts are left out on purpose):

| Where | Setting |
|-------|---------|
| Fonts | Interface `Maple Normal UI`, monospace `Maple Mono Normal NFM` |
| Icons | Everforest-Dark |
| Windows | Minimize / maximize buttons hidden, theme applied to GNOME apps |
| Terminal | Maple Mono 15 (weights 500 / bold 800 / dim 300), 77% opacity, no header bar, Noir |

Install the [Maple fonts](https://github.com/subframe7536/maple-font) and the
icons (see Icons below) and import the terminal scheme first, then:

```bash
./cosmic/install.sh
```

It backs up each file it replaces to `*.bak` and COSMIC applies it live.

---

## COSMIC Terminal

The desktop `.ron` does not colour ANSI text.

1. COSMIC Terminal → **View → Color schemes…** (not Settings → Appearance)
2. Dark tab → **Import** → `cosmic-term/Noir-term.ron`
3. View → Settings → Appearance → Color scheme (dark) → **Noir**

If a profile is set as default, set the scheme on that profile too or the
dropdown will look like it did nothing.

Fog text on charcoal; orange for errors and the cursor, sage for strings and
success, khaki in the yellow slot, grey-sage for directories.

---

## Firefox

Built-in **Dark** theme plus the stylesheets in `firefox/chrome/`.

```bash
./firefox/install.sh
```

Fully quit Firefox afterward. Details and CSS rules: [`firefox/README.md`](firefox/README.md).

---

## Cursor

**Oxygen-02-Vibrant-Orange**, patched with the cursor names COSMIC apps ask
for. COSMIC has no cursor picker yet, so the script sets it:

```bash
./cursors/install.sh
reboot
```

Why the patch, what the script touches and how to undo it:
[`cursors/README.md`](cursors/README.md).

---

## Scripts

### `update_system.sh`

nala + flatpak updater. Headers in orange, info in grey-sage, success in sage,
errors in orange; the banner ramps from khaki to orange.

```bash
chmod +x scripts/update_system.sh
./scripts/update_system.sh
```

---

## Terminal extras

Need a [Nerd Font](https://www.nerdfonts.com/) in the terminal for the icons
(Maple Mono NFM in the baseline above).

### zsh

`zsh/noir.zsh` is the rice part of the shell only: `LS_COLORS` (also used by
lsd for file names and by the completion menu), orange / sage / khaki colours
for zsh-autosuggestions and zsh-syntax-highlighting, lsd / bat / nvim aliases
and the starship prompt. Your own `~/.zshrc` stays private and sources it.

Needs zsh + [oh-my-zsh](https://ohmyz.sh/). `install.sh` clones the two
plugins if missing and appends one `source` line to `~/.zshrc` (backup in
`~/.zshrc.bak`):

```bash
./zsh/install.sh
exec zsh
```

In `~/.zshrc` keep `ZSH_THEME=""` and
`plugins=(git sudo zsh-autosuggestions zsh-syntax-highlighting)`.

### lsd

File names are coloured by `LS_COLORS` from `zsh/noir.zsh`;
`lsd/colors.yaml` colours the other columns with the 256-colour codes nearest
the palette (202 orange, 208 ember, 108 sage, 144 khaki, 246 grey-sage,
243 muted, 240 dim). lsd 1.0.0 does not accept `#hex` there.

```bash
./lsd/install.sh
lsd -l
```

### fastfetch

COSMIC logo in orange, Hardware / Software / Age boxes in dim grey with
grey-sage keys. `install.sh` backs up any existing
`~/.config/fastfetch/config.jsonc` to `config.jsonc.bak`.

```bash
./fastfetch/install.sh
fastfetch
```

### btop

`btop/Noir.theme`: charcoal background, dim grey boxes, orange titles, meters
ramp from sage through khaki to orange.

```bash
mkdir -p ~/.config/btop/themes
cp btop/Noir.theme ~/.config/btop/themes/
# btop → Esc → Options → Color theme → Noir
```

---

## Icons and wallpaper

Icons: **Everforest-Dark** from
[Fausto-Korpsvart/Everforest-GTK-Theme](https://github.com/Fausto-Korpsvart/Everforest-GTK-Theme):

```bash
git clone --depth 1 https://github.com/Fausto-Korpsvart/Everforest-GTK-Theme.git
mkdir -p ~/.local/share/icons
cp -r Everforest-GTK-Theme/icons/Everforest-Dark ~/.local/share/icons/
gtk-update-icon-cache -f ~/.local/share/icons/Everforest-Dark
# Settings → Desktop → Appearance → Icons → Everforest-Dark
```

Wallpapers live in [cool-wallpapers](https://github.com/atraxsrc/cool-wallpapers).

Two wallpapers made for this rice, recoloured from the COSMIC astronaut and the
Harbor Dark reaper so they sit on the exact window background:

| File | What it is |
|------|------------|
| [`cosmic-astronaut-noir-3840x2160.png`](https://github.com/atraxsrc/cool-wallpapers/blob/main/cosmic/cosmic-astronaut-noir-3840x2160.png) | COSMIC astronaut in grey-sage with orange lines on charcoal |
| [`reaper-skull-noir-3440x1440.png`](https://github.com/atraxsrc/cool-wallpapers/blob/main/reaper/reaper-skull-noir-3440x1440.png) | Reaper in khaki and orange on charcoal |

From the upstream theme, folder
[`omarchy/greek-noir/`](https://github.com/atraxsrc/cool-wallpapers/tree/main/omarchy/greek-noir)
(MIT, licence in the folder):

| File | What it is |
|------|------------|
| [`greek-noir-bg1-3840x2400.png`](https://github.com/atraxsrc/cool-wallpapers/blob/main/omarchy/greek-noir/greek-noir-bg1-3840x2400.png) | Figure sinking into dark olive water |
| [`greek-noir-bg3-3840x2160.png`](https://github.com/atraxsrc/cool-wallpapers/blob/main/omarchy/greek-noir/greek-noir-bg3-3840x2160.png) | Small botanical engravings on dark olive |
| [`greek-noir-bg2-4096x2905.jpg`](https://github.com/atraxsrc/cool-wallpapers/blob/main/omarchy/greek-noir/greek-noir-bg2-4096x2905.jpg) | Soldier and black wolf, grey background |

Settings → Wallpaper → Add image → the file you downloaded.

---

## Setup

```bash
git clone https://github.com/atraxsrc/cosmic-noir-theme.git
cd cosmic-noir-theme

# desktop
# Settings → Appearance → Dark → Import cosmic/Noir.ron

# terminal
# View → Color schemes → Import cosmic-term/Noir-term.ron

# firefox
./firefox/install.sh

# cursor (then reboot), see cursors/README.md
./cursors/install.sh

# shell + terminal tools (see Terminal extras above)
./zsh/install.sh
./lsd/install.sh
./fastfetch/install.sh
mkdir -p ~/.config/btop/themes && cp btop/Noir.theme ~/.config/btop/themes/

# wallpaper
# Settings → Wallpaper → Add image → a file from
# https://github.com/atraxsrc/cool-wallpapers/tree/main/omarchy/greek-noir

# icons (see Icons above) + Maple fonts (https://github.com/subframe7536/maple-font), then
# fonts, icons, terminal look from cosmic/config/
./cosmic/install.sh
```

---

## Stack

| Tool | What it does |
|------|-------------|
| [Pop!_OS 24.04](https://pop.system76.com/) | Base OS by System76 |
| [COSMIC DE](https://system76.com/cosmic) | Desktop environment |
| [oh-my-zsh](https://ohmyz.sh/) | zsh framework + plugins |
| [lsd](https://github.com/lsd-rs/lsd) | `ls` with icons and colours |
| [fastfetch](https://github.com/fastfetch-cli/fastfetch) | System info |
| [btop](https://github.com/aristocratos/btop) | Resource monitor |
| [Everforest-GTK-Theme](https://github.com/Fausto-Korpsvart/Everforest-GTK-Theme) | Icon pack (Everforest-Dark) |
| [Oxygen-Cursors](https://github.com/wo2ni/Oxygen-Cursors) | Cursor (vibrant orange) |

## Credits

- Palette and wallpapers: [omarchy-greek-noir-theme](https://github.com/HANCORE-linux/omarchy-greek-noir-theme)
  by HANCORE-linux (MIT). This repo is a COSMIC port; the wallpapers are
  mirrored in cool-wallpapers, not here.
- Light half: [cosmic-dossier-theme](https://github.com/atraxsrc/cosmic-dossier-theme).
  Shared baseline (frosted glass, squared corners, fonts) from
  [cosmic-darkgold-theme](https://github.com/atraxsrc/cosmic-darkgold-theme).

## License

MIT. The cursor artwork keeps the terms of KDE's Oxygen project, see
[`cursors/README.md`](cursors/README.md).
