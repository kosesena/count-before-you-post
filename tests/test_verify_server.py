"""Exercise the HTTP upload boundary without model calls or ERP credentials."""
import base64
import http.client
import io
import json
import tempfile
import threading
import time
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from cbyp.verify_server import make_server
from cbyp.workflow import verify

class VerificationServer(unittest.TestCase):
    def setUp(self):
        self.called=[]
        def runner(note,camera,audio,order,language,progress):
            self.called.append((note,camera,audio))
            self.assertTrue(all(p.is_file() for p in (note,camera,audio)))
            progress('Checking')
            return {'mode':'dry_run','erp_written':False,'decision':{'action':'human'}}
        self.temp=tempfile.TemporaryDirectory()
        self.root=patch('cbyp.verify_server.ROOT',Path(self.temp.name));self.root.start()
        self.server=make_server(0,runner)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.token=self.request('GET','/api/config')[1]['token']
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.server.worker_pool.shutdown()
        self.thread.join();self.root.stop();self.temp.cleanup()
    def request(self,method,path,payload=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        h={'Content-Type':'application/json','X-Verification-Token':getattr(self,'token','')}
        h.update(headers or {})
        c.request(method,path,json.dumps(payload) if payload is not None else None,h)
        r=c.getresponse();status=r.status;data=json.loads(r.read());c.close();return status,data
    def payload(self):
        b=io.BytesIO();Image.new('RGB',(4,4)).save(b,format='PNG')
        pic={'name':'input.png','base64':base64.b64encode(b.getvalue()).decode()}
        b=io.BytesIO()
        with wave.open(b,'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\x00\x00'*160)
        return {'consent':True,'language':'Turkish','order':{'number':'PO-1','supplier':'Test','product':'Oil','ordered':12,'received':0},'note':pic,'camera':pic,'audio':{'name':'receiver.wav','base64':base64.b64encode(b.getvalue()).decode()}}
    def test_rejects_cross_origin_and_missing_token_before_runner(self):
        for headers in ({'Origin':'https://example.com'},{'X-Verification-Token':''},{'Host':'example.com'}):
            self.assertEqual(self.request('POST','/api/verify',self.payload(),headers)[0],403)
        self.assertEqual(self.called,[])
    def test_invalid_inputs_never_invoke_models(self):
        for key,value in [('consent',False),('camera',{'name':'x.png','base64':'broken'}),('order',{'number':'x'})]:
            p=self.payload();p[key]=value
            self.assertEqual(self.request('POST','/api/verify',p)[0],400)
        self.assertEqual(self.called,[])
    def test_upload_report_and_cleanup(self):
        status,job=self.request('POST','/api/verify',self.payload());self.assertEqual(status,202)
        for _ in range(100):
            status,result=self.request('GET','/api/jobs/'+job['id'])
            if result['status']!='running':break
            time.sleep(.01)
        self.assertEqual(result['status'],'complete');self.assertFalse(result['result']['erp_written'])
        self.assertEqual(len(self.called),1)
        self.server.worker_pool.shutdown()
        self.assertTrue(all(not p.exists() for p in self.called[0]))
        self.assertTrue((Path(self.temp.name)/'.local-verification'/f"{job['id']}.json").is_file())
    def test_missing_files_fail_before_models(self):
        with patch('cbyp.workflow.full_session') as factory:
            with self.assertRaises(ValueError):verify('absent','absent','absent',self.payload()['order'])
            factory.assert_not_called()
