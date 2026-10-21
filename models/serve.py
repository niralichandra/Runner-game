"""Local preview server that never lets the browser reuse an old copy of the page."""
import http.server, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()


http.server.ThreadingHTTPServer(('', PORT), NoCache).serve_forever()
