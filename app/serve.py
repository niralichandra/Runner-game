"""Serves the Run folder (game in /app, your models in /models) without browser caching."""
import http.server, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NoCache(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.glb': 'model/gltf-binary', '.js': 'text/javascript', '.json': 'application/json'}

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, *args):
        pass


print(f'Rail Rush running at http://localhost:{PORT}/app/  (close this window to stop)')
http.server.ThreadingHTTPServer(('', PORT), NoCache).serve_forever()
