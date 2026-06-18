find src -type f -name '*.ui' -print0 | while IFS= read -r -d '' ui; do
  dir="$(dirname "$ui")"
  base="$(basename "$ui" .ui)"
  poetry run pyuic6 "$ui" -o "$dir/ui_${base}.py"
done