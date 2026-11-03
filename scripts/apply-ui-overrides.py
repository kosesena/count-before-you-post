import hashlib,json
from pathlib import Path
root=Path('site/i18n');p=root/'translations.json';rows=json.loads(p.read_text())
for text,overrides in json.loads((root/'overrides.json').read_text()).items():
 key=hashlib.sha256(text.encode()).hexdigest()[:16]
 rows.setdefault(key,{'id':key}).update(overrides)
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
