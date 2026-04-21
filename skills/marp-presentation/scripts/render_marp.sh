#!/usr/bin/env sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: render_marp.sh <deck.md> <pdf|pptx|html> [output]"
  exit 1
fi

deck_path="$1"
fmt="$2"
output_path="${3:-}"

if [ -x "./node_modules/.bin/marp" ]; then
  base_cmd="./node_modules/.bin/marp"
elif command -v marp >/dev/null 2>&1; then
  base_cmd="marp"
else
  base_cmd="npx @marp-team/marp-cli@latest"
fi

case "$fmt" in
  pdf) flag="--pdf" ;;
  pptx) flag="--pptx" ;;
  html) flag="" ;;
  *)
    echo "unsupported format: $fmt"
    exit 1
    ;;
esac

browser_args=""
if [ "$fmt" = "pdf" ] && [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  browser_args="--browser-path /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome"
fi

if [ -n "$output_path" ]; then
  # shellcheck disable=SC2086
  exec sh -c "$base_cmd \"$deck_path\" $flag -o \"$output_path\" $browser_args"
else
  # shellcheck disable=SC2086
  exec sh -c "$base_cmd \"$deck_path\" $flag $browser_args"
fi
