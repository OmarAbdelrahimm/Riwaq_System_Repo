# -*- coding: utf-8 -*-
"""Applies the v2.1 corrections to beats.json (surgical, auditable)."""
import json, copy
B = json.load(open('beats.json', encoding='utf-8'))
by = {}
for b in B:
    by.setdefault(b['line'], []).append(b)
for k in by: by[k].sort(key=lambda x: x['i'])

# 1) break the three long graphic runs with human-scale inserts
by[19].append({"line":19,"i":99,"type":"HUMAN","visual":"نافذة كوخ عند الفجر: كتف رجل يمرّ خلف الزجاج المغبش، لا وجه","cam":"doorway light · slow push","txt":""})
by[71].append({"line":71,"i":99,"type":"WIDE","visual":"حقل أوروبي من بعيد تحت سحاب منخفض: ثلاث قطع أرض مختلفة الظل، لا بشر","cam":"slow push 3% · wind","txt":""})
by[108].append({"line":108,"i":99,"type":"HUMAN","visual":"طاولة مكتوبة: أصابع تمسك قلمًا فوق ورق، ظل اليد يغطي نصف الصفحة","cam":"rack focus · pencil shadow","txt":""})
# 2) split the 10.8 s villa hold (line 83) — hold keeps 4.5 s, tail becomes a storm detail
by[83].append({"line":83,"i":99,"type":"DETAIL","visual":"مزراب حجري يصبّ ماءً على الأرض المبلولة، رذاذ عند الاصطدام","cam":"rack focus · splash","txt":""})
# 3) soften the 4-in-a-row WIDE at 151..154
by[127][0]["type"] = "SILHOUETTE"
# 4) re-balance two all-graphic scenes with one human beat each
by[14].append({"line":14,"i":99,"type":"HUMAN","visual":"ظل مزارع يقف عند طرف الحقل، القبعة في يده، الظهر للكاميرا","cam":"drift · wind","txt":""})
by[124].append({"line":124,"i":99,"type":"HUMAN","visual":"يد تضع كوب شاي على ورقة تقويم فارغة، البخار يعبر الورق","cam":"rack focus · steam","txt":""})

out=[]
for ln in sorted(by):
    for i,b in enumerate(by[ln]):
        b=copy.deepcopy(b); b['i']=i; out.append(b)
json.dump(out, open('beats.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("beats now:", len(out))
