# Cosmic Noir for Cursor

A colour theme for [Cursor](https://cursor.com) from the
[COSMIC Noir](https://github.com/atraxsrc/cosmic-noir-theme) rice: charcoal
editor, grey-sage neutrals, sage strings and one loud orange. It is a plain
VS Code theme extension, so VS Code and VSCodium take it too.

## Install

```bash
./vscode/install.sh                # Cursor
./vscode/install.sh code codium    # VS Code / VSCodium instead
```

It packs this folder into `vscode/cosmic-noir-theme-<version>.vsix` and
installs that with the editor's CLI (`cursor --install-extension`), so the
theme is listed under Extensions and running the script again updates it.
Then press <kbd>Ctrl</kbd>+<kbd>K</kbd> <kbd>Ctrl</kbd>+<kbd>T</kbd> and pick
**Cosmic Noir**.

No CLI on the PATH (an AppImage, say): the script still builds the `.vsix`;
install it from Extensions → `...` → **Install from VSIX**.

## What it colours

Code is coloured the way Neovim is in this rice (`nvim/colors/noir.lua`):

| Role | Colour | Hex |
|------|--------|-----|
| Keywords, tags | Orange | `#F25623` |
| Functions, tag attributes | Khaki | `#AEAB94` |
| Strings | Sage | `#88A57D` |
| Numbers, constants | Ember | `#F56E0F` |
| Types, classes, modules | Grey-sage | `#959C95` |
| Imports, macros, decorators, escapes, `this` / `self` | Amber | `#F0913A` |
| Parameters | Light grey, italic | `#A6ADA6` |
| Operators, punctuation | Muted | `#7D837D` |
| Comments | Dim, italic | `#686C69` |

The workbench uses the surfaces of `cosmic/Noir.ron`: charcoal `#171717` for
the editor, side bars, panel, title and status bar, soot `#222222` for
menus, hovers, inputs and the command palette, slate `#2A2A2A` for borders
and the selected row. The active tab and the active activity bar icon get an
orange line. Menus highlight in orange with charcoal text, like the Firefox
stylesheets. The integrated terminal uses the COSMIC Terminal scheme
(`cosmic-term/Noir-term.ron`), so command output looks the same as in COSMIC
Terminal.

Cursor's own panels (Agent, chat, inline diffs) have no colour keys of
their own. Cursor builds them from standard ones, and the theme sets those:
the button colour is the agent's accent (orange, with charcoal text), the
side bar and panel colours are its surfaces, the diff colours are its
accept / reject highlights (sage added, orange removed), and the terminal's
`blue` slot (ember) colours its links.

Errors share the orange, as everywhere in this rice. Warnings are ember and
info is grey-sage.

## Contrast

Text is at least 4.5:1 on its background, checked with a script over the
text and background pairs the theme sets. The exceptions are the dim greys
the Neovim scheme uses too: comments, line numbers and AI ghost text are
3.4:1 (comments 3.2:1 on the current line), inlay hints 4.1:1, and operators
4.3:1 on the current line.
