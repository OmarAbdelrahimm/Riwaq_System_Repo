#!/usr/bin/env python3
"""Local read-only preflight; 0 GPU / 0 AI credits / 0 renders."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
contract=json.loads((ROOT/'config/asset_contract.json').read_text(encoding='utf-8'))
missing=[]
for a in contract['assets']:
 p=ROOT/a['path'] if a.get('path') else None
 status='FOUND' if p and p.is_file() else 'MISSING'
 sha=hashlib.sha256(p.read_bytes()).hexdigest()[:12] if status=='FOUND' else '-'
 print(f"{status:7} {a['id']:20} {sha}  declared:{a['status']}  {a.get('path') or '[not supplied]'}")
 if status=='MISSING': missing.append(a['id'])
print('\nFILES STILL MISSING:', ', '.join(missing) or 'none')
print('Note: missing visual originals and S01 audio may be present outside this handoff, in the agent repo.')
