from http.server import BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Route the request
        if self.path == '/health':
            response = b'{"status": "healthy"}'
        elif self.path == '/':
            response = b'{"message": "API is running", "status": "ok"}'
        else:
            self.send_response(404)
            response = b'{"error": "Not found"}'
        
        self.wfile.write(response)