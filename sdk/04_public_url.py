"""Start a web server inside the sandbox and get a token-protected HTTPS address for it."""
import time
import urllib.request

from _env import check_env
from wbxsandbox import Sandbox

check_env()

APP = '''
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type", "text/plain"); self.end_headers()
        self.wfile.write(b"Hello from a WBX sandbox\\n")
HTTPServer(("0.0.0.0", 8000), H).serve_forever()   # listen on 0.0.0.0, not 127.0.0.1
'''

with Sandbox.create(timeout=300) as sb:
    sb.files.write("/home/user/app.py", APP)
    sb.run("nohup python3 /home/user/app.py >/tmp/app.log 2>&1 &", timeout=5).check()
    time.sleep(1)

    link = sb.get_url(8000)
    print("open in a browser:", link["url_with_token"])

    req = urllib.request.Request(link["url"], headers={"X-WBX-Token": link["token"]})
    print("fetched:", urllib.request.urlopen(req, timeout=15).read().decode().strip())

    input("Press Enter to stop the app and destroy the sandbox... ")
