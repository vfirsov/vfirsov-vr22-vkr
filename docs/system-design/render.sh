#!/usr/bin/env sh
# Перерисовывает диаграммы: src/*.mmd → img/*.svg и img/*.png (PNG — в 2× для слайдов и Word).
# Нужен Node.js; mermaid-cli скачивается через npx.
# Свой бинарь mmdc — в переменной MMDC, свой конфиг Puppeteer (например, executablePath) — в PUPPETEER_CONFIG.
set -eu
cd "$(dirname "$0")"
MMDC=${MMDC:-"npx -y @mermaid-js/mermaid-cli@11.4.2"}
mkdir -p img
for src in src/*.mmd; do
  name=$(basename "$src" .mmd)
  for out in "img/$name.svg" "img/$name.png"; do
    $MMDC -q -c mermaid.config.json ${PUPPETEER_CONFIG:+-p "$PUPPETEER_CONFIG"} \
      -b white -w 2400 -s 2 -i "$src" -o "$out"
  done
  echo "$name"
done
