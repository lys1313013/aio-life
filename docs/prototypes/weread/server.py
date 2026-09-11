"""Local-only WeRead prototype. Run: python3 server.py"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import os
import time
import threading

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get('WEREAD_PREVIEW_PORT', '8765'))
ORIGIN = f'http://127.0.0.1:{PORT}'
ALLOWED = {'/shelf/sync', '/readdata/detail', '/user/notebooks',
           '/book/bookmarklist', '/review/list/mine', '/book/getprogress'}
cache = {}
lock = threading.Lock()

def key():
    value = os.environ.get('WEREAD_API_KEY', '')
    if not value and (ROOT / '.env').exists():
        for line in (ROOT / '.env').read_text().splitlines():
            if line.startswith('WEREAD_API_KEY='):
                value = line.split('=', 1)[1].strip()
    return value

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send(self, status, data, content_type='application/json; charset=utf-8'):
        raw = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(raw)

    def local(self):
        return self.headers.get('Host') == f'127.0.0.1:{PORT}'

    def do_GET(self):
        if not self.local():
            return self.send(403, {'error': '仅允许本机预览'})
        if self.path in ('/', '/index.html'):
            return self.send(200, (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/health':
            return self.send(200, {'ready': bool(key())})
        if self.path == '/requirements':
            return self.send(200, (ROOT / '开发需求.md').read_bytes(), 'text/plain; charset=utf-8')
        return self.send(404, {'error': '页面不存在'})

    def do_POST(self):
        if not self.local() or self.headers.get('Origin') != ORIGIN or self.headers.get('X-Preview') != '1':
            return self.send(403, {'error': '仅允许本地页面调用'})
        if self.path != '/api':
            return self.send(404, {'error': '接口不存在'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192:
                return self.send(400, {'error': '请求大小无效'})
            body = json.loads(self.rfile.read(length))
            name = body.get('api_name')
            if name not in ALLOWED:
                return self.send(400, {'error': '不支持此接口'})
            params = {'api_name': name, 'skill_version': '1.0.4'}
            for field in ('mode', 'baseTime', 'bookId', 'bookid', 'count', 'lastSort', 'synckey'):
                if field in body:
                    params[field] = body[field]
            token = key()
            if not token:
                return self.send(401, {'error': '请在本机 .env 中配置 WEREAD_API_KEY 后重试'})
            signature = json.dumps(params, sort_keys=True)
            with lock:
                entry = cache.get(signature)
            if entry and time.time() - entry[0] < 300 and not body.get('refresh'):
                return self.send(200, entry[1])
            request = Request('https://i.weread.qq.com/api/agent/gateway',
                              data=json.dumps(params).encode(),
                              headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
            with urlopen(request, timeout=25) as response:
                data = json.load(response)
            if data.get('errcode') not in (None, 0, '0'):
                return self.send(502, {'error': '微信读书返回错误：' + str(data.get('errmsg', data['errcode'])).replace(token, '[已隐藏]')})
            with lock:
                cache[signature] = (time.time(), data)
            return self.send(200, data)
        except HTTPError as exc:
            message = 'Key 无效或已过期，请更新本机配置' if exc.code in (401, 403) else f'微信读书请求失败（HTTP {exc.code}），请稍后重试'
            return self.send(502, {'error': message})
        except (URLError, TimeoutError):
            return self.send(502, {'error': '连接微信读书超时或网络不可用，请重试'})
        except (ValueError, TypeError):
            return self.send(400, {'error': '请求或响应格式无效'})

if __name__ == '__main__':
    print(f'WeRead preview: {ORIGIN}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
