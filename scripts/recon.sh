#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$(awk -F': ' '/^target:/ {print $2; exit}' "$ROOT/scope.yml" | tr -d '\r' | xargs)"
if [[ -z "$TARGET" || "$TARGET" == "target.com" ]]; then echo 'Set an authorized target in scope.yml'; exit 1; fi
RUN="$(date -u +%Y-%m-%d_%H-%M-%S)"
OUT="$ROOT/results/$RUN"
LATEST="$ROOT/results/latest"
mkdir -p "$OUT" "$LATEST"
rm -rf "$LATEST"/*

echo "[+] crt.sh"
curl -fsSL "https://crt.sh/?q=%25.${TARGET}&output=json" | jq -r '.[].name_value' 2>/dev/null | sed 's/^\*\.//' | sort -u > "$OUT/crtsh.txt" || true

echo "[+] subfinder"
subfinder -d "$TARGET" -silent 2>/dev/null | sort -u > "$OUT/subfinder.txt" || true
printf '%s\n%s\n%s\n' "$TARGET" "$TARGET" "$TARGET" >> "$OUT/all-hosts.tmp"
cat "$OUT/crtsh.txt" "$OUT/subfinder.txt" >> "$OUT/all-hosts.tmp" || true
sed 's/^\*\.//' "$OUT/all-hosts.tmp" | sort -u | grep -E "(^|\.)${TARGET//./\.}$" > "$OUT/hosts.txt" || true
rm -f "$OUT/all-hosts.tmp"

echo "[+] dnsx"
dnsx -l "$OUT/hosts.txt" -silent -a -resp 2>/dev/null > "$OUT/dnsx.txt" || true

echo "[+] httpx"
httpx -l "$OUT/hosts.txt" -silent -follow-redirects -status-code -title -tech-detect -rate-limit 5 > "$OUT/live.txt" 2>/dev/null || true

echo "[+] katana"
cut -d' ' -f1 "$OUT/live.txt" | sed 's/\[.*//' | sort -u | head -n 50 | katana -silent -jc -d 2 -rl 5 > "$OUT/js-endpoints.txt" 2>/dev/null || true

cat > "$OUT/summary.txt" <<SUM
Target: $TARGET
Run: $RUN
Hosts: $(wc -l < "$OUT/hosts.txt" | tr -d ' ')
Live services: $(wc -l < "$OUT/live.txt" | tr -d ' ')
JS/endpoints: $(wc -l < "$OUT/js-endpoints.txt" | tr -d ' ')

Automation is reconnaissance/passive discovery only.
SUM
cp -a "$OUT/." "$LATEST/"
cat "$OUT/summary.txt"
