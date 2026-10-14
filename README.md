<div align="center">

# COSMIC · Noir

Pop!_OS 24.04 on COSMIC in charcoal, sage and orange: desktop, terminal,
shell, Firefox, cursor, wallpapers. The dark half of a pair; the light half is
[cosmic-dossier-theme](https://github.com/atraxsrc/cosmic-dossier-theme).

![Pop!_OS](https://img.shields.io/badge/Pop!_OS-24.04_LTS-f25623?style=for-the-badge&logo=popos&logoColor=white)
![COSMIC](https://img.shields.io/badge/COSMIC-1.0.0-88a57d?style=for-the-badge)
![Noir](https://img.shields.io/badge/Theme-Noir-171717?style=for-the-badge&labelColor=f25623)
![Firefox](https://img.shields.io/badge/Firefox-Noir-f25623?style=for-the-badge&logo=firefox-browser&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-7d837d?style=for-the-badge)

</div>

---
![Pop!_OS COSMIC desktop with the Noir theme](assets/screenshot.png)

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
│   ├── Noir-term.ron            # COSMIC Terminal colour scheme
│   ├── Noir-term-*.ron          # dimmer plain-text variants, same ANSI colours
│   └── README.md                # previews and which one to pick
├── cursors
│   ├── Oxygen-Noir-*/            # cursor themes, one per icon colour, patched for COSMIC apps
│   ├── install.sh
│   ├── uninstall.sh
│   └── README.md
├── icons
│   └── install.sh               # Cosmic-Noir icon pack from cosmic-icon-themes
├── fastfetch
│   ├── config.jsonc             # orange / grey-sage fastfetch config
│   ├── cosmic.txt               # COSMIC logo
│   └── install.sh
├── firefox
│   ├── theme                    # Cosmic Noir theme add-on (manifest + icons)
│   ├── chrome
│   │   ├── userChrome.css       # rounded chrome, soot menus
│   │   └── userContent.css      # new tab accent
│   ├── install.sh
│   └── README.md
├── lsd
│   ├── config.yaml              # theme: custom
│   ├── colors.yaml              # permission / size / date / git columns
│   └── install.sh
├── nvim                         # Neovim colorscheme, LazyVim spec, RON syntax, install.sh
├── scripts
│   └── update_system.sh         # nala + flatpak, orange / sage ANSI
├── zsh
│   ├── noir.zsh                 # LS_COLORS, highlighting colours, aliases, starship
│   └── install.sh
├── assets
│   ├── cursors/                 # cursor preview
│   ├── cosmic-term/             # scheme previews for cosmic-term/README.md
│   ├── screenshot.png           # README screenshot
│   └── wallpaper.png            # the anime portrait on the bare desktop
├── backgrounds/                 # wallpapers, noir-<subject>.png (see Icons and wallpaper)
├── docs
│   └── showcase.md              # the rice describing itself, for the Postilla pane of the screenshot
├── LICENSE
└── README.md
```

---

## COSMIC Desktop

Settings → Desktop → Appearance → **Dark** → **Import** → `cosmic/Noir.ron`

Accent is orange `#F25623`. Use the `+` control if you want a custom swatch.

Frosted glass is on in the `.ron` at `frosted: Low` with an opacity table of
0.66 to 0.96, tinted with the palette's middle neutral, for windows, panel,
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
| Fonts | Interface `Maple Normal UI` Light, monospace `Maple Mono Normal NFM` |
| Icons | Cosmic-Noir-Orange |
| Windows | Minimize / maximize buttons hidden, theme applied to GNOME apps |
| Terminal | Maple Mono 15 (weights 500 / bold 800 / dim 300), 77% opacity, no header bar, Noir |

Install the [Maple fonts](https://github.com/subframe7536/maple-font) and the
Cosmic-Noir icons (see Icons below) and import the terminal scheme first, then:

```bash
./cosmic/install.sh
```

It backs up each file it replaces to `*.bak` and COSMIC applies it live.

The interface font is the Light weight on purpose. COSMIC sets interface text
brightness itself (the text tint only picks the hue), so on these dark panels
labels land near `#DFE7DF` whatever tint you choose; the thinner strokes are
what calms them at night. Settings → Fonts lists only families, so the weight
lives in `cosmic/config/com.system76.CosmicTk/v1/interface_font`.

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

If fog glares at night, there are five dimmer variants with the same ANSI
colours, from Smoke `#7D837D` up to Pale `#BCBFBC`. Previews and which to
pick: [`cosmic-term/README.md`](cosmic-term/README.md).

---

## Firefox

Two layers:

1. **Theme (colours):** install
   **[cosmic-noir-theme on addons.mozilla.org](https://addons.mozilla.org/en-US/firefox/addon/cosmic-noir-theme/)**.
   This is the main look.
2. **Stylesheets (optional):** `firefox/chrome/` adds rounded corners, orange
   menu hover, orange accents and blank new-tab tiles on top of the add-on
   (they also work with Firefox's built-in Dark theme):

```bash
./firefox/install.sh
```

Fully quit Firefox afterward. Details and CSS rules: [`firefox/README.md`](firefox/README.md).

---

## Cursor

**Oxygen** cursors recoloured to the icon colours, one per folder colour of the
Cosmic-Noir icon pack: **Orange** (default), **Sage**, **Dark**. Patched with the cursor
names COSMIC apps ask for. COSMIC has no cursor picker yet, so the script sets it:

```bash
./cursors/install.sh                      # Orange
./cursors/install.sh --variant Sage      # or another, see --list
reboot
```

Previews, what the script touches, how to undo it and how the colours are made:
[`cursors/README.md`](cursors/README.md).

---

## Scripts

### `update_system.sh`

nala + flatpak updater. Headers in orange, info in grey-sage, success in sage,
errors in orange; the banner ramps from sage to fog, orange only in the rule below it.

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

### Neovim

`nvim/` carries the rice into Neovim: a dependency-free colorscheme built from
the palette (`nvim/colors/noir.lua`), a LazyVim spec that selects it and makes
sure the treesitter parsers for the files in this repo are installed
(`nvim/lua/plugins/noir.lua`), and a small RON syntax file so `cosmic/*.ron`
is coloured even before the parser exists. `:terminal` inside Neovim uses the
Noir scheme.

```bash
./nvim/install.sh
# restart nvim; LazyVim switches to the noir colorscheme
```

Without LazyVim, copy `nvim/colors/noir.lua` to `~/.config/nvim/colors/` and
run `:colorscheme noir`.

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

Icons: **Cosmic-Noir**, the [Kanagawa icons](https://github.com/Fausto-Korpsvart/Kanagawa-GKT-Theme/tree/main/icons/Kanagawa)
by Fausto Korpsvart recolored to this palette in
[cosmic-icon-themes](https://github.com/atraxsrc/cosmic-icon-themes). Folders come in
three colors: **Orange** `#F25623` (default), **Sage** `#88A57D` and **Dark** `#2A2A2A` with orange symbols.

![Cosmic-Noir folder colors](https://raw.githubusercontent.com/atraxsrc/cosmic-icon-themes/main/previews/Cosmic-Noir.png)

```bash
./icons/install.sh                 # Orange folders
./icons/install.sh --variant Sage  # or Dark
```

It downloads the pack from the latest cosmic-icon-themes release, checks its SHA256,
installs it to `~/.local/share/icons/` and sets it as the COSMIC icon theme.
Restart open apps afterwards (Files caches icons per window).
Add `--system` to install to `/usr/share/icons` instead, for every user and the
login screen (asks for sudo); `--user` is the default.

Wallpapers ship in [`backgrounds/`](backgrounds/), named `noir-<subject>.png`:
the thirteen subjects every dark rice has, rendered in sage and orange on charcoal:
the Harbor Dark reaper and Hyundai blueprint, the COSMIC astronaut, the samurai,
sushi switch, geisha, JS mug and neon street from the Tokyo Night set, The Greek
eagle and ink portrait, and three new scenes: city, panel and tower.
The anime portrait (`noir-anime.png`) is the one in the screenshot.
The subjects come from [HANCORE-linux](https://github.com/HANCORE-linux) (MIT) and
[cool-wallpapers](https://github.com/atraxsrc/cool-wallpapers); each was rendered again in this palette, then upscaled.
More from the upstream theme in cool-wallpapers, folder
[`omarchy/greek-noir/`](https://github.com/atraxsrc/cool-wallpapers/tree/main/omarchy/greek-noir) (MIT).

Settings → Wallpaper → Add image → a file from `backgrounds/`, or one you downloaded.

![The anime portrait wallpaper on the Noir desktop, panel only](assets/wallpaper.png)

---

## Setup

```bash
git clone https://github.com/atraxsrc/cosmic-noir-theme.git
cd cosmic-noir-theme

# desktop
# Settings → Appearance → Dark → Import cosmic/Noir.ron

# terminal
# View → Color schemes → Import cosmic-term/Noir-term.ron

# firefox add-on
# https://addons.mozilla.org/en-US/firefox/addon/cosmic-noir-theme/

# optional extra chrome
./firefox/install.sh

# cursor (then reboot), see cursors/README.md
./cursors/install.sh                      # Orange
./cursors/install.sh --variant Sage      # or another, see --list
reboot

# shell + terminal tools (see Terminal extras above)
./zsh/install.sh
./lsd/install.sh
./fastfetch/install.sh
./nvim/install.sh
mkdir -p ~/.config/btop/themes && cp btop/Noir.theme ~/.config/btop/themes/

# wallpaper
# Settings → Wallpaper → Add image → a file from backgrounds/ (see Icons and wallpaper above)

./icons/install.sh                  # icons (see Icons above)
# Maple fonts (https://github.com/subframe7536/maple-font), then
# fonts, icons, terminal look from cosmic/config/
./cosmic/install.sh
```

---

## Switching rice

The installers replace what they own (with a `*.bak` copy), but three things
pile up instead of being replaced: shell layers in `~/.zshrc`, LazyVim specs and
the updater link. Coming to Noir from another rice:

1. **Desktop, terminal, Firefox, cursor, icons:** run [Setup](#setup) as usual.
   Disable the old rice's Firefox add-on before enabling this one.
2. **zsh:** `./zsh/install.sh` adds a Noir `source` line but leaves the old one.
   In `~/.zshrc` keep exactly one rice line active, at the end. Comment out any
   `ricing/zsh/colors.zsh` line too (cosmic-ricing re-adds it when it applies a theme).
3. **Neovim:** LazyVim loads every spec in `lua/plugins/`, and the last one that
   sets a colorscheme wins, so an old rice's spec can override Noir. Park the
   others outside `lua/plugins/`:

   ```bash
   mkdir -p ~/.config/nvim/rice-off
   cd ~/.config/nvim/lua/plugins && ls     # anything besides noir.lua and your own specs?
   mv darkgold.lua ~/.config/nvim/rice-off/   # once per old rice spec
   ```

   Then `:Lazy clean` removes plugins only those specs used. Files in `colors/`
   can stay; they do nothing until a spec selects them.
4. **Updater:** point `~/update_system.sh` at this rice's script:

   ```bash
   ln -sfn "$PWD/scripts/update_system.sh" ~/update_system.sh
   ```

5. **btop:** Esc → Options → Color theme → Noir.
6. `exec zsh`, restart Neovim and Firefox, reboot for the cursor.

Leaving Noir is the same list in reverse: the next rice's Setup, then swap the
zsh line, the LazyVim spec and the updater link. `./cursors/uninstall.sh` puts
the Pop cursor back.

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
| [cosmic-icon-themes](https://github.com/atraxsrc/cosmic-icon-themes) | Icon pack (Cosmic-Noir), recolored from [Kanagawa icons](https://github.com/Fausto-Korpsvart/Kanagawa-GKT-Theme/tree/main/icons/Kanagawa) |
| [Oxygen-Cursors](https://github.com/wo2ni/Oxygen-Cursors) | Cursor, recoloured to the icon colours |

## Credits

- Palette and wallpapers: [omarchy-greek-noir-theme](https://github.com/HANCORE-linux/omarchy-greek-noir-theme)
  by HANCORE-linux (MIT). This repo is a COSMIC port; the upstream wallpapers
  are mirrored in cool-wallpapers, the renders for this palette are in `backgrounds/`.
- Light half: [cosmic-dossier-theme](https://github.com/atraxsrc/cosmic-dossier-theme).
  Shared baseline (frosted glass, squared corners, fonts) from
  [cosmic-darkgold-theme](https://github.com/atraxsrc/cosmic-darkgold-theme).

## License

MIT. The cursor artwork keeps the terms of KDE's Oxygen project, see
[`cursors/README.md`](cursors/README.md).
