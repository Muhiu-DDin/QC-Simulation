"""Run the manual-entry web interface locally: python serve.py."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from api.calculate import handler

ROOT=Path(__file__).resolve().parent
class LocalHandler(SimpleHTTPRequestHandler):
    send_json=handler.send_json
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'vercel-site'),**kwargs)
    def do_POST(self):
        if self.path.split('?')[0] in ('/api/calculate','/api/calculate.py'): handler.do_POST(self)
        else: self.send_json(404,{'error':'Unknown endpoint'})
    def do_GET(self):
        if self.path.split('?')[0] in ('/api/calculate','/api/calculate.py'): handler.do_GET(self)
        else: super().do_GET()

if __name__=='__main__':
    print('Open http://127.0.0.1:8000/calculator.html — press Ctrl+C to stop.',flush=True)
    try: ThreadingHTTPServer(('127.0.0.1',8000),LocalHandler).serve_forever()
    except KeyboardInterrupt: pass
