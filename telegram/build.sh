#!/usr/bin/env bash
# Build cosmic-noir.tdesktop-theme for Telegram Desktop: a zip of
# colors.tdesktop-theme plus the chat background. The default background is
# plain charcoal; --wallpaper puts one of backgrounds/*.png behind the chat,
# re-encoded to a 2560px JPEG (ImageMagick) to stay under Telegram's 5 MB limit.
#   ./telegram/build.sh
#   ./telegram/build.sh --wallpaper backgrounds/noir-anime.png
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$DIR/cosmic-noir.tdesktop-theme"
WALLPAPER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wallpaper) WALLPAPER="${2:?--wallpaper needs a .png or .jpg}"; shift 2 ;;
    -h|--help) sed -n 2,7p "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done
if [[ -n "$WALLPAPER" && ! -f "$WALLPAPER" ]]; then
  echo "no such file: $WALLPAPER" >&2
  exit 1
fi

# Telegram refuses theme files over 5 MB; the wallpapers are bigger than that
LIMIT=$((5 * 1024 * 1024))
if [[ -n "$WALLPAPER" ]] && command -v convert >/dev/null 2>&1; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  convert "$WALLPAPER" -resize '2560x2560>' -strip -quality 90 "$TMP/background.jpg"
  WALLPAPER="$TMP/background.jpg"
fi

python3 -I - "$DIR/colors.tdesktop-theme" "$OUT" "$WALLPAPER" <<'EOF'
import struct, sys, zipfile, zlib

colors, out, wallpaper = sys.argv[1:4]

def solid_png(rgb):
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data)))
    raw = b"\x00" + bytes(rgb)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw))
            + chunk(b"IEND", b""))

if wallpaper:
    name = "background.jpg" if wallpaper.lower().endswith((".jpg", ".jpeg")) else "background.png"
    background = open(wallpaper, "rb").read()
else:
    name, background = "background.png", solid_png((0x17, 0x17, 0x17))

# fixed timestamps so a rebuild of the same input is byte-identical
stamp = (2026, 1, 1, 0, 0, 0)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for arcname, data in (("colors.tdesktop-theme", open(colors, "rb").read()), (name, background)):
        info = zipfile.ZipInfo(arcname, stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, data)
EOF

if (( $(stat -c %s "$OUT") > LIMIT )); then
  rm -f "$OUT"
  echo "theme is over Telegram's 5 MB limit; install ImageMagick (convert) or pass a smaller image" >&2
  exit 1
fi
echo "  built $OUT"
echo
echo "In Telegram Desktop: Settings -> Chat Settings -> Chat wallpaper ->"
echo "Choose from file -> pick cosmic-noir.tdesktop-theme -> Apply this theme."
