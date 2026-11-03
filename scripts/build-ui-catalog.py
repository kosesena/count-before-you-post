"""Extract UI text and apply maintained translations. --translate calls the configured Meta API.
Build dependency: acorn 8.19.0 (use NODE_PATH for a temporary installation).
"""
import os,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='cbyp-i18n-') as tmp:
 env=dict(os.environ,CBYP_I18N_EXTRACT=str(Path(tmp)/'strings.json'))
 files=[str(p.relative_to(root)) for p in (root/'site').rglob('*') if p.suffix in ('.html','.js','.mjs') and not any(x in p.parts for x in ('i18n','vendor','models')) and '.test.' not in p.name and p.name!='original-report.html']
 subprocess.run(['node','scripts/extract-ui-strings.cjs',*files],cwd=root,env=env,check=True)
 subprocess.run([sys.executable,'scripts/collect-ui-strings.py'],cwd=root,env=env,check=True)
 subprocess.run([sys.executable,'scripts/apply-ui-overrides.py'],cwd=root,env=env,check=True)
 if '--translate' in sys.argv:
  subprocess.run([sys.executable,'scripts/translate-ui.py'],cwd=root,env=env,check=True)
  subprocess.run([sys.executable,'scripts/apply-ui-overrides.py'],cwd=root,env=env,check=True)
