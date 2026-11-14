#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""textgate.py — every string a chapter can draw, checked against the fact sheet.

Three failure modes are caught here, and all three shipped at least once in this project:

  1. a banned figure reaching the glass (VEI, a death toll, the 3 C number, the
     1790-1820 window);
  2. a number in Arabic type that has no verified row in the fact sheet -- a figure the
     narration does not support;
  3. a font that silently falls back, so a card is measured but comes out empty. Each
     string is rendered and its ink counted, and the resolved face is reported.

    python textgate.py 3 4 5 6
"""
import ast
import csv
import os
import re
import sys

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AR = re.compile(r'[\u0600-\u06ff]')
DIGIT = re.compile(r'[0-9\u0660-\u0669]')
# Arabic-Indic digits are what the on-screen type actually uses; the sheet records the
# same figure in ASCII. Compare them as the same number, or every verified date fails.
AR2ASCII = {chr(0x0660 + i): str(i) for i in range(10)}

BANS = {
    'VEI': ['VEI', 'مؤشر الانفجار'],
    '~3C': ['3°', '٣°', '3 C', 'ثلاث درجات'],
    '1790w': ['1790', '١٧٩٠', '1820', '١٨٢٠'],
    'deaths': ['60,000', '10,000', '80,000', '٦٠٠٠٠', '١٠٠٠٠', '٨٠٠٠٠', '60 ألف'],
    '1of6': ['1 من 6', '١ من ٦', 'واحد من ستة'],
    'km3': ['150', '٤٣ كم', '43 كم', '60 Mt'],
}


def strings(path):
    tree = ast.parse(open(path, encoding='utf-8').read())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if AR.search(s):
                out.append((node.lineno, s))
    return out


def allowed(rows):
    ok = set()
    for r in rows[1:]:
        if len(r) < 6:
            continue
        if r[5] in ('VERIFIED', 'VERIFY-LINK') and r[3] == 'نعم':
            for m in DIGIT.findall(r[0]) or []:
                pass
            num = ''.join(AR2ASCII.get(c, c) for c in DIGIT.findall(r[0]))
            if num:
                ok.add(num)
    return ok


def ink_ok(s):
    from eng5 import core5 as C
    for fname in ('Amiri-Regular.ttf', 'Amiri-Bold.ttf'):
        sp = C.text_sprite(s, size=40, fname=fname)
        a = sp.split()[3]
        n = sum(1 for v in a.tobytes() if v > 8)
        if n < 12:
            return False, fname, n
    return True, 'Amiri', -1


def main(ns):
    rows = list(csv.reader(open(os.path.join(ROOT, 'FACT_CHECK_SHEET.csv'),
                                encoding='utf-8-sig')))
    ok_nums = allowed(rows)
    fail = 0
    for n in ns:
        p = os.path.join(ROOT, f'ch{n}', 'eng', f'ch{n}v5.py')
        for line, s in strings(p):
            hits = [k for k, pats in BANS.items() if any(b in s for b in pats)]
            digits = [AR2ASCII.get(c, c) for c in DIGIT.findall(s)]
            blank, face, cnt = ink_ok(s)
            problems = []
            if hits:
                problems.append('BANNED ' + ','.join(hits))
            if digits:
                joined = ''.join(digits)
                if joined not in ok_nums:
                    problems.append('UNVERIFIED NUMBER ' + joined)
            if not blank:
                problems.append('NO INK from ' + face)
            if problems:
                fail += 1
                print(f'  ch{n}:{line}  {s[:64]}')
                for pr in problems:
                    print(f'      -> {pr}')
    print('TEXTGATE', 'FAIL %d' % fail if fail else 'PASS')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main([int(a) for a in sys.argv[1:]] or [3, 4, 5, 6]))
