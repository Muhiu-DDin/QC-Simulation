"""Vercel Python function and shared request handler for the local web server."""
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler
os.environ.setdefault('MPLCONFIGDIR',os.path.join(tempfile.gettempdir(),'qc-matplotlib'))
from qc.web_service import evaluate

class handler(BaseHTTPRequestHandler):
    def send_json(self,status,payload):
        encoded=json.dumps(payload,allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(encoded)))
        self.end_headers(); self.wfile.write(encoded)

    def do_GET(self): self.send_json(200,{'status':'ready','service':'Python quality-control calculator'})

    def do_POST(self):
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=131072:
                self.send_json(413,{'error':'Provide a dataset smaller than 128 KB.'}); return
            payload=json.loads(self.rfile.read(length))
            self.send_json(200,evaluate(payload))
        except (ValueError,TypeError,KeyError,OverflowError) as error:
            self.send_json(400,{'error':str(error)})
