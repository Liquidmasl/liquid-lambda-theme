# Cosmic Noir for Cursor

A dark colour theme for [Cursor](https://cursor.com) from this rice: **Cosmic Noir**.
It is a plain VS Code theme extension, so VS Code and VSCodium take it too.

## Install

```bash
./vscode/install.sh                # Cursor
./vscode/install.sh code codium    # VS Code / VSCodium instead
```

It packs this folder into `vscode/cosmic-noir-theme-<version>.vsix` and installs
that with the editor's CLI (`cursor --install-extension`), so the theme is
listed under Extensions and running the script again updates it. Then press
<kbd>Ctrl</kbd>+<kbd>K</kbd> <kbd>Ctrl</kbd>+<kbd>T</kbd> and pick **Cosmic Noir**.

No CLI on the PATH (an AppImage, say): the script still builds the `.vsix`;
install it from Extensions → `...` → **Install from VSIX**.

## What it colours

Code is coloured the way Neovim is in the rice (`nvim/colors/*.lua`):

| Role | Noir |
|------|------ |
| Keywords, tags | ![#F25623](https://placehold.co/12x12/F25623/F25623.png) `#F25623` |
| Functions, tag attributes | ![#AEAB94](https://placehold.co/12x12/AEAB94/AEAB94.png) `#AEAB94` |
| Strings | ![#88A57D](https://placehold.co/12x12/88A57D/88A57D.png) `#88A57D` |
| Numbers, constants | ![#F56E0F](https://placehold.co/12x12/F56E0F/F56E0F.png) `#F56E0F` |
| Types, classes, modules | ![#959C95](https://placehold.co/12x12/959C95/959C95.png) `#959C95` |
| Imports, macros, decorators, escapes, `this` / `self` | ![#F0913A](https://placehold.co/12x12/F0913A/F0913A.png) `#F0913A` |
| Parameters (italic) | ![#A6ADA6](https://placehold.co/12x12/A6ADA6/A6ADA6.png) `#A6ADA6` |
| Operators, punctuation | ![#7D837D](https://placehold.co/12x12/7D837D/7D837D.png) `#7D837D` |
| Comments (italic) | ![#686C69](https://placehold.co/12x12/686C69/686C69.png) `#686C69` |
| Accent | ![#F25623](https://placehold.co/12x12/F25623/F25623.png) `#F25623` |

The workbench takes the window colour of the rice's `cosmic/*.ron` for the
editor, side bars, panel, title and status bar, the container colours for
menus, hovers, inputs and the command palette, and the accent for the active
tab line, buttons, badges and the menu highlight. The integrated terminal uses
the rice's COSMIC Terminal scheme (`cosmic-term/`), so command output looks the
same as in COSMIC Terminal.

Cursor's own panels (Agent, chat, inline diffs) have no colour keys of their
own. Cursor builds them from standard ones, and the theme sets those: the
button colour is the agent's accent, the side bar and panel colours are its
surfaces, the diff colours are its accept / reject highlights, and the
terminal's `blue` slot colours its links.

## Contrast

Text is at least 4.5:1 on the window background and on menus and hovers,
comments and line numbers at least 3:1, checked with a script over the text
and background pairs the theme sets.
On the highlighted current line, code can dip slightly under 4.5:1 and
comments under 3:1.
