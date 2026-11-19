#!/bin/bash
# usage: ./go.sh NAME 'order' 'order' ...   adds the orders (all or none) and plays on.
#        ./go.sh NAME                        shows where the fight stands.
#        BOARD=0 ./go.sh ...                 hides the map.
name=$1; shift
touch "$name.orders"; cp "$name.orders" "$name.orders.bak"
for o in "$@"; do printf '%s\n' "$o" >> "$name.orders"; done
out=$(python3 table.py "$name" 2>&1)
if printf '%s' "$out" | grep -q "ORDER PROBLEM\|Traceback"; then
  cp "$name.orders.bak" "$name.orders"
  printf '%s\n' "$out" | grep -A12 "ORDER PROBLEM\|Traceback" | head -30
  echo ">>> None of these orders were added. Fix and run again."
else
  if [ "$BOARD" = "0" ]; then printf '%s\n' "$out" | grep -Ev '^ +[0-9]+ [#.A-Za-z=o~>]{6,}$|^    0123'; else printf '%s\n' "$out"; fi
fi
