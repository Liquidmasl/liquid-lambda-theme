#!/usr/bin/env bash
# Make the Lambda-Cursors theme active. Build it first with `uv run lambda apply`
# (it lands in ~/.local/share/icons/Lambda-Cursors).
#
#   ./cursors/install.sh                  # also copy to /usr/share/icons (login screen, Flatpak)
#   ./cursors/install.sh --user           # use the copy in ~/.local/share/icons only
#   ./cursors/install.sh --size 32        # cursor size (default 24)
#
# COSMIC has no cursor picker yet, so the theme is set with XCURSOR_THEME in
# /etc/environment, which cosmic-comp reads at login. The theme carries the
# cursor names COSMIC apps ask for (default, ew-resize, ...) as symlinks.
#
# Backs up every config file it changes (.bak-<timestamp>). Safe to run again.
set -euo pipefail

THEME="Lambda-Cursors"
BUILT="${XDG_DATA_HOME:-$HOME/.local/share}/icons/$THEME"
SIZE="${XCURSOR_SIZE_OVERRIDE:-24}"
DEST="/usr/share/icons"
USER_MODE=false
STAMP="$(date +%Y%m%d-%H%M%S)"

usage() {
  sed -n '2,7s/^# \{0,1\}//p' "${BASH_SOURCE[0]}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)    USER_MODE=true ;;
    --size)    SIZE="${2:-}"; shift ;;
    --size=*)  SIZE="${1#--size=}" ;;
    -h|--help) usage; exit 0 ;;
    *)         echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
  shift
done
[[ "$SIZE" =~ ^[0-9]+$ ]] || { echo "Size must be a number, got '$SIZE'"; exit 1; }
[[ -f "$BUILT/index.theme" ]] || { echo "$BUILT not found; run: uv run lambda apply --only cursors"; exit 1; }

# 1. system copy, for the login screen and Flatpak apps -----------------------
if $USER_MODE; then
  echo "Using $BUILT"
elif [[ -d "$DEST/$THEME" ]] && diff -r --no-dereference -q "$BUILT" "$DEST/$THEME" >/dev/null 2>&1; then
  echo "  $DEST/$THEME already up to date"
else
  echo "Copying to $DEST (needs sudo)"
  # build next to the target, then swap, so a failed copy never leaves half a theme
  tmp="$DEST/.$THEME.new-$$"
  sudo rm -rf -- "$tmp"
  sudo mkdir -p "$tmp"
  sudo cp -R -P "$BUILT/." "$tmp/"
  sudo chmod -R a+rX "$tmp"
  [[ -d "$DEST/$THEME" ]] && sudo rm -rf -- "${DEST:?}/$THEME"
  sudo mv -- "$tmp" "$DEST/$THEME"
  echo "  installed $DEST/$THEME"
fi

# 2. cosmic-comp reads XCURSOR_* from /etc/environment at login ---------------
want="$(printf 'XCURSOR_THEME=%s\nXCURSOR_SIZE=%s' "$THEME" "$SIZE")"
have="$(grep -E '^XCURSOR_(THEME|SIZE)=' /etc/environment 2>/dev/null || true)"
if [[ "$have" == "$want" ]]; then
  echo "/etc/environment already set to $THEME, size $SIZE"
else
  echo "Setting XCURSOR_THEME=$THEME XCURSOR_SIZE=$SIZE in /etc/environment (needs sudo)"
  sudo cp -p /etc/environment "/etc/environment.bak-$STAMP"
  sudo sed -i '/^XCURSOR_THEME=/d;/^XCURSOR_SIZE=/d' /etc/environment
  printf '%s\n' "$want" | sudo tee -a /etc/environment >/dev/null
  echo "  backup: /etc/environment.bak-$STAMP"
fi

# 3. X11 / XWayland apps -----------------------------------------------------
idx="$HOME/.icons/default/index.theme"
new_idx="$(printf '[Icon Theme]\nInherits=%s' "$THEME")"
if [[ -f "$idx" && "$(cat "$idx")" == "$new_idx" ]]; then
  echo "$idx already inherits $THEME"
else
  mkdir -p "$(dirname "$idx")"
  if [[ -f "$idx" ]]; then
    cp -p "$idx" "$idx.bak-$STAMP"
    echo "  backup: $idx.bak-$STAMP"
  fi
  printf '%s\n' "$new_idx" > "$idx"
  echo "Wrote $idx"
fi

# 4. GTK apps ----------------------------------------------------------------
if command -v gsettings >/dev/null; then
  gsettings set org.gnome.desktop.interface cursor-theme "$THEME" 2>/dev/null || true
  gsettings set org.gnome.desktop.interface cursor-size "$SIZE" 2>/dev/null || true
fi

# 5. Flatpak apps don't see /etc/environment ---------------------------------
if command -v flatpak >/dev/null; then
  flatpak override --user --env=XCURSOR_THEME="$THEME" --env=XCURSOR_SIZE="$SIZE" || true
fi

echo
echo "Active: $THEME (size $SIZE)"
echo "Reboot (or log out and back in): cosmic-comp only reads the cursor at startup."
