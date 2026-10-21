#!/usr/bin/env bash
# يرندر الشورتس التسعة بالتتابع ثم يبني حزم النشر — سجلّ واضح لكل خطوة.
set -u
cd /home/user/Riwaq_System_Repo/scripts/series
source env.sh >/dev/null 2>&1
python3 build_shorts.py assets 2>&1 | tail -1
for k in S01 S02 S03 S04 S05 S06 S07 S08 S09; do
  echo "=== $k $(date +%H:%M:%S)"
  python3 build_shorts.py render "$k" 2>&1 | tail -1
  python3 shorts_pack.py "$k" 2>&1 | tail -1
done
echo "ALL_SHORTS_DONE"
