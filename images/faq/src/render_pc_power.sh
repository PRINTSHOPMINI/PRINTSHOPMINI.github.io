#!/bin/bash
# FAQ 그림 PC 전원 버튼(삼성·HP·켜는 법) PNG 만들기 — 2026-11-03. 실행: bash images/faq/src/render_pc_power.sh
H="$(cd "$(dirname "$0")" && pwd -W)"
OUT="$(cd "$(dirname "$0")/.." && pwd)"
CH="/c/Program Files/Google/Chrome/Application/chrome.exe"
PROF="$TEMP/pc_power_chrome"
shot(){ timeout 90 "$CH" --headless=new --user-data-dir="$PROF" --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=$2 --virtual-time-budget=8000 --allow-file-access-from-files --screenshot="$1" "file:///$H/pc-power.html?s=$3" >/dev/null 2>&1; }
shot "$OUT/pc-power-samsung.png" 900,820 samsung
shot "$OUT/pc-power-samsung-side.png" 900,820 samsungside
shot "$OUT/pc-power-hp.png" 900,820 hp
shot "$OUT/pc-power-how.png" 900,560 how
ls -la "$OUT"/pc-power-*.png
