"""Local-only new-input verification UI. python -m cbyp.verify_server [--port 8768]
Model calls require an explicit Run click. This server has no ERP writer or sign-off endpoint.
"""
import argparse
import base64
import io
import json
import secrets
import tempfile
import threading
import wave
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image
from .workflow import verify

ROOT=Path(__file__).resolve().parents[1]
LIMIT=24*1024*1024


def decode_file(item,kind,directory):
    data=base64.b64decode(item['base64'],validate=True)
    if not data or len(data)>6*1024*1024:raise ValueError('Each file must be 1 byte–6 MB.')
    suffix=Path(item['name']).suffix.lower()
    if kind=='audio':
        if suffix!='.wav':raise ValueError('Receiver audio must be WAV.')
        with wave.open(io.BytesIO(data)) as w:
            if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getframerate()!=16000:
                raise ValueError('WAV must be mono, 16-bit, 16 kHz.')
            if w.getnframes()/w.getframerate()>90:raise ValueError('Maximum audio length is 90 seconds.')
    elif kind=='note' and suffix=='.pdf':
        if not data.startswith(b'%PDF-'):raise ValueError('Invalid PDF.')
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            if not 1<=len(pdf.pages)<=3:raise ValueError('Use a 1–3 page note.')
    else:
        if suffix not in ('.png','.jpg','.jpeg'):raise ValueError('Use a JPEG or PNG image.')
        with Image.open(io.BytesIO(data)) as im:
            if im.width*im.height>25_000_000:raise ValueError('Image too large.')
            im.verify()
    path=Path(directory)/(kind+suffix);path.write_bytes(data);return path


def make_server(port=8768,runner=verify):
    jobs={};lock=threading.Lock();pool=ThreadPoolExecutor(max_workers=1)
    token=secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,status,data,ctype='application/json'):
            raw=json.dumps(data,ensure_ascii=False).encode() if ctype=='application/json' else data
            self.send_response(status);self.send_header('Content-Type',ctype)
            self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)
        def trusted(self):
            allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            if self.headers.get('Host') not in allowed:return False
            origin=self.headers.get('Origin')
            return not origin or origin in {'http://'+h for h in allowed}
        def do_GET(self):
            if not self.trusted():return self.reply(403,{'error':'Local access only.'})
            if self.path in ('/','/index.html'):
                return self.reply(200,(ROOT/'site/verify/index.html').read_bytes(),'text/html; charset=utf-8')
            if self.path=='/api/config':return self.reply(200,{'token':token,'mode':'dry_run'})
            if self.path.startswith('/api/jobs/'):
                if self.headers.get('X-Verification-Token')!=token:return self.reply(403,{'error':'Invalid session.'})
                with lock:job=dict(jobs.get(self.path.split('/')[-1],{}))
                return self.reply(200 if job else 404,job or {'error':'Not found.'})
            return self.reply(404,{'error':'Not found.'})
        def do_POST(self):
            if not self.trusted() or self.headers.get('X-Verification-Token')!=token:
                return self.reply(403,{'error':'Invalid local session.'})
            if self.path!='/api/verify':return self.reply(404,{'error':'Not found.'})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=LIMIT:return self.reply(413,{'error':'Upload too large.'})
                payload=json.loads(self.rfile.read(length))
                if payload.get('consent') is not True:raise ValueError('Confirm model processing first.')
                if payload.get('language') not in ('Turkish','English','German','Chinese'):raise ValueError('Choose a supported language.')
                order=payload['order']
                if not all(isinstance(order.get(k),str) and order[k].strip() for k in ('number','supplier','product')):raise ValueError('Complete the trusted order fields.')
                if any(type(order.get(k)) is not int or order[k]<0 for k in ('ordered','received')) or order['received']>order['ordered']:raise ValueError('Invalid order quantities.')
                temp=tempfile.TemporaryDirectory(prefix='cbyp-')
                try:files={k:decode_file(payload[k],k,temp.name) for k in ('note','camera','audio')}
                except Exception as e:
                    temp.cleanup()
                    raise ValueError('Invalid upload: use a readable image/PDF and mono 16 kHz WAV.') from e
            except (ValueError,KeyError,TypeError, OSError) as e:
                return self.reply(400,{'error':str(e)[:180]})
            with lock:
                if any(j['status']=='running' for j in jobs.values()):
                    temp.cleanup();return self.reply(409,{'error':'One verification is already running.'})
                ident=secrets.token_hex(12);jobs[ident]={'status':'running','step':'Starting'}
            def work():
                def progress(step):
                    with lock:jobs[ident]['step']=step
                try:
                    result=runner(files['note'],files['camera'],files['audio'],order,payload['language'],progress)
                    out=ROOT/'.local-verification';out.mkdir(exist_ok=True)
                    (out/f'{ident}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
                    with lock:jobs[ident]={'status':'complete','result':result}
                except Exception as e:
                    # Provider errors may include file contents/URLs; never echo them to the page.
                    with lock:jobs[ident]={'status':'error','error':'Verification stopped; no ERP write. Check model access and input files.','error_type':type(e).__name__}
                finally:temp.cleanup()
            pool.submit(work)
            self.reply(202,{'id':ident})
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.worker_pool=pool
    return server

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8768);a=p.parse_args()
    server=make_server(a.port)
    print(f'New-input verification: http://127.0.0.1:{server.server_port} — dry run only',flush=True)
    try:server.serve_forever()
    finally:server.server_close();server.worker_pool.shutdown()
