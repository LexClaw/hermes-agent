#!/usr/bin/env python3
import json, sys, pathlib
manifest = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'lex-customizations-manifest.json')
data = json.loads(manifest.read_text())
fail=[]
for e in data.get('entries', []):
    p = pathlib.Path(e['path'])
    check = e.get('check','path-exists')
    if check == 'directory-exists':
        if not p.is_dir(): fail.append(f"{e['path']}: directory missing")
        continue
    if not p.exists():
        fail.append(f"{e['path']}: path missing")
        continue
    if check.startswith('grep:'):
        marker=check.split(':',1)[1]
        if p.is_dir():
            hay='\n'.join(x.read_text(errors='ignore') for x in p.rglob('*') if x.is_file())
        else:
            hay=p.read_text(errors='ignore')
        if marker not in hay:
            fail.append(f"{e['path']}: marker {marker!r} missing")
if fail:
    print('Manifest check FAILED')
    for f in fail: print('FAIL:', f)
    sys.exit(1)
print(f"Manifest check passed: {len(data.get('entries', []))} entries")
