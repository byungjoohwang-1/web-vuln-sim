#!/bin/sh
# Rebuild the static Tailwind CSS used by the sim pages (replaces the dev
# cdn.tailwindcss.com Play CDN, which is not for production). Re-run after
# adding/removing Tailwind utility classes in any sim*.html.
# Output: public/css/tailwind.css (linked by the 21 swapped pages).
# Note: sim-xxe.html intentionally still uses the CDN (custom tailwind.config + forms plugin).
set -e
cd "$(dirname "$0")/.."
npx -y tailwindcss@3.4.17 -i ./_gen/_tw_input.css -o ./public/css/tailwind.css \
  --content "./public/sim*.html,./public/03_code_processvalidation.html" --minify
echo "built public/css/tailwind.css"
