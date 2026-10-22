#!/usr/bin/env bash
# يرندر الحلقات 04–06 ثم يبني حزم النشر — سجل واضح لكل خطوة.
set -u
cd /home/user/Riwaq_System_Repo/scripts/series
source env.sh >/dev/null 2>&1
for k in EP04 EP05 EP06; do
  echo "=== $k $(date +%H:%M:%S)"
  python3 build_ep.py prep "$k"  2>&1 | tail -1
  python3 build_ep.py render "$k" 2>&1 | tail -1
  python3 ep_pack.py "$k"         2>&1 | tail -1
done
echo "ALL_EPISODES_DONE"
