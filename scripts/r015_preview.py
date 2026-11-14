"""Loopback visual test fixture. No shop, Stripe or InPost network calls."""
import http.server,json,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,unquote
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'.artifacts/r015-local';E.mkdir(parents=True,exist_ok=True)
options=json.loads(re.search(r'id="winter-options">([^<]+)',(ROOT/'winter-zestaw-4.html').read_text(encoding='utf-8')).group(1))
stock={m['id']+':'+v['colorId']:100 for m in options['models'] for v in m['variants']}
stock['full-soft:red-matte']=0
status={'mode':'test','available':True,'currency':'PLN','freeCourierFromOrnaments':6,'smallOrderCourierGrosz':2049,'locker_available':True,'locker_amount_grosze':1849,'geowidget_token':None,'points_provider':'mock','points_notice':'TEST / MOCK — bez połączenia z InPost','test_points':[{'id':i,'label':i} for i in ['TEST01M','TEST02M']],'stock':stock}
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
    def log_message(self,*a):pass
    def json(self,code,value):
        self.send_response(code);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(value).encode())
    def do_GET(self):
        u=urlsplit(self.path);path=unquote(u.path)
        if path=='/api/status.php':self.json(200,status);return
        if path=='/api/pickup-point.php':
            point=parse_qs(u.query).get('id',[''])[0]
            if point not in ('TEST01M','TEST02M'):self.json(422,{'message':'Punkt testowy niedostępny.'});return
            self.json(200,{'id':point,'provider':'mock','notice':status['points_notice'],'address':status['points_notice']+' — Syntetyczny adres '+point});return
        if path.startswith('/api/') or '/.' in path or not path.endswith(('.html','.js','.css','.webp','.avif','.jpg','.png','.svg')) and path!='/':self.send_error(404);return
        if path in ('/','/index.html'):self.path='/winter-26.html'
        super().do_GET()
    def do_POST(self):
        if self.path!='/api/checkout.php':self.send_error(404);return
        n=int(self.headers.get('Content-Length','0'));assert 0<=n<=16384
        data=json.loads(self.rfile.read(n));log=E/'checkout-attempts.json'
        rows=json.loads(log.read_text()) if log.exists() else []
        rows.append({'number':len(rows)+1,'delivery':data.get('delivery_method'),'selections':len(data.get('selections',[])),'hasRequestId':bool(data.get('requestId'))})
        log.write_text(json.dumps(rows,indent=2),encoding='utf-8')
        self.json(422,{'code':'LOCAL_TEST','message':'Lokalny test zakończony — nie utworzono płatności.'})
    def end_headers(self):
        self.send_header('Cache-Control','no-store');self.send_header('X-Robots-Tag','noindex, noarchive')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'")
        super().end_headers()
http.server.ThreadingHTTPServer(('127.0.0.1',8796),Handler).serve_forever()
