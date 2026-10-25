# Liquid Lambda for Cursor / VS Code

A dark colour theme for [Cursor](https://cursor.com) generated from `palette.toml`: **Liquid Lambda**.
It is a plain VS Code theme extension, so VS Code and VSCodium take it too.

## Install

```bash
./vscode/install.sh                # Cursor
./vscode/install.sh code codium    # VS Code / VSCodium instead
```

It packs this folder into `vscode/liquid-lambda-theme-<version>.vsix` and installs
that with the editor's CLI (`cursor --install-extension`), so the theme is
listed under Extensions and running the script again updates it. Then press
<kbd>Ctrl</kbd>+<kbd>K</kbd> <kbd>Ctrl</kbd>+<kbd>T</kbd> and pick **Liquid Lambda**.

No CLI on the PATH (an AppImage, say): the script still builds the `.vsix`;
install it from Extensions → `...` → **Install from VSIX**.

## What it colours

Code colours by palette role (`templates/vscode/themes/lambda-color-theme.json.j2`):

| Role | Code |
|------|------|
| `lead` | Keywords, tags, the accent (active tab line, buttons, badges) |
| `second` toward `text` | Functions, tag attributes |
| `ok` | Strings |
| `second` | Numbers, constants |
| `sub` toward `lead` | Types, classes, modules |
| `amber_bright` | Imports, macros, decorators, escapes, `this` / `self` |
| `sub` | Parameters (italic) |
| `muted` | Operators, punctuation |
| `dim` | Comments (italic) |

The workbench takes the palette's window colour for the
editor, side bars, panel, title and status bar, the container colours for
menus, hovers, inputs and the command palette, and the accent for the active
tab line, buttons, badges and the menu highlight. The integrated terminal uses
the palette's 16 ANSI colours, so command output looks the same as in WezTerm.

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
