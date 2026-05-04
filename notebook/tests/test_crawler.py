import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# make workspace root importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib.util

# import crawler module by file path (not a package)
mod_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Modules', 'crawler.py'))
spec = importlib.util.spec_from_file_location('crawler_module', mod_path)
crawler_module = importlib.util.module_from_spec(spec)

# provide a minimal requests shim using urllib to avoid external dependency
import types
import urllib.request

class _Response:
    def __init__(self, text, status=200):
        self.text = text
        self.status_code = status
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

def _requests_get(url, timeout=10, headers=None):
    req = urllib.request.Request(url, headers=(headers or {}))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        text = data.decode('utf-8', errors='ignore')
        status = getattr(r, 'status', 200)
        return _Response(text, status)

requests_shim = types.SimpleNamespace(get=_requests_get)
import sys as _sys
_sys.modules['requests'] = requests_shim

spec.loader.exec_module(crawler_module)
Clowler = crawler_module.Clowler


def run_server(directory):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    with TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        print(f"Serving on port {port}")
        # run until shutdown is called
        httpd.serve_forever()


def start_server_in_thread(directory):
    server = TCPServer(("127.0.0.1", 0), SimpleHTTPRequestHandler)
    port = server.server_address[1]

    def serve():
        os.chdir(directory)
        try:
            server.serve_forever()
        finally:
            server.server_close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return server, port


def main():
    base_dir = os.path.join(os.path.dirname(__file__), "static")
    server, port = start_server_in_thread(base_dir)
    time.sleep(0.2)

    start_url = f"http://127.0.0.1:{port}/index.html"

    c = Clowler()
    results = c.crawl_domain(start_url, "決算", max_depth=2, return_dom=True)

    # Expect both index.html and page2.html to be found
    assert isinstance(results, list), "results should be a list"
    urls = {r["url"] for r in results}
    assert any("index.html" in u for u in urls), "index.html should be in results"
    assert any("page2.html" in u for u in urls), "page2.html should be in results"

    for r in results:
        assert "soup" in r and "matches" in r, "each result must contain soup and matches"
        assert len(r["matches"]) >= 1, "matches should contain at least one matched line"

    print("TEST PASSED: crawler returned DOMs for all matched pages")

    server.shutdown()


if __name__ == "__main__":
    main()
