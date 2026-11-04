"""Password-protected, synchronous hosted dry run. Never writes ERP or persists uploads."""
from http.server import BaseHTTPRequestHandler
import hmac,json,os,tempfile
from urllib.parse import urlparse

MAX_BODY=4_000_000

def process(payload, runner=None):
    from cbyp.verify_server import decode_file
    from cbyp.workflow import verify
    from cbyp.counting_area import select_area, attach_area
    if not isinstance(payload,dict) or payload.get('consent') is not True:
        raise ValueError('Confirm model processing first.')
    if payload.get('language') not in ('Turkish','English','German','Chinese'):
        raise ValueError('Choose a supported audio language.')
    with tempfile.TemporaryDirectory(prefix='cbyp-hosted-') as tmp:
        files={k:decode_file(payload[k],k,tmp) for k in ('note','camera','audio')}
        files['camera'], area = select_area(files['camera'], payload.get('counting_area'), tmp)
        if area is not None and len(json.dumps(area).encode()) > 4_000_000:
            raise ValueError('Original and selected area exceed hosted evidence size; use the local service.')
        order=payload['order']
        if not isinstance(order,dict):raise ValueError('Invalid trusted order.')
        order=dict(order,require_supplier=True)
        return attach_area((runner or verify)(*(files[k] for k in ('note','camera','audio')),order,payload['language']), area)

class handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,status,data):
        raw=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        self.reply(200,{'mode':'hosted_dry_run','requires_access_code':True,'max_body_bytes':MAX_BODY,
                       'configured':all(os.environ.get(k) for k in ('VERIFICATION_ACCESS_CODE','META_API_KEY','BASETEN_API_KEY'))})
    def drain(self):
        # Read a rejected request's body first, or the client sees a reset instead of the 403
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:return
        if 0<length<=MAX_BODY:self.rfile.read(length)
    def do_POST(self):
        secret=os.environ.get('VERIFICATION_ACCESS_CODE','')
        supplied=self.headers.get('X-Verification-Token','')
        if not secret or not hmac.compare_digest(secret.encode(),supplied.encode()):
            self.drain();return self.reply(403,{'error':'Valid demo access code required.'})
        origin=self.headers.get('Origin')
        if origin and urlparse(origin).netloc!=self.headers.get('Host'):
            self.drain();return self.reply(403,{'error':'Use the verification page on this site.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=MAX_BODY:return self.reply(413,{'error':'Combined upload too large (4 MB encoded limit). Use smaller files or the local workflow.'})
            payload=json.loads(self.rfile.read(length))
            result=process(payload)
        except (ValueError,KeyError,TypeError,OSError):
            return self.reply(400,{'error':'Invalid inputs or processing stopped. No ERP write. Check files and order; retry starts a fresh run.'})
        except Exception:
            return self.reply(502,{'error':'Model verification could not finish. No ERP write. Retry starts a fresh run and may incur new usage.'})
        self.reply(200,result)
