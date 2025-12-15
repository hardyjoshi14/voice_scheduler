from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Try to import FastAPI - if it fails, we'll still have working endpoints
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
    print("✅ FastAPI imports successful")
except ImportError as e:
    FASTAPI_AVAILABLE = False
    print(f"⚠️ FastAPI not available: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/health':
            response = b'{"status": "healthy", "framework": "BaseHTTPRequestHandler"}'
        elif self.path == '/':
            response = b'{"message": "Voice Scheduler API", "status": "ok", "framework": "BaseHTTPRequestHandler"}'
        elif self.path == '/fastapi-test':
            if FASTAPI_AVAILABLE:
                response = b'{"message": "FastAPI is available!", "status": "ok"}'
            else:
                response = b'{"error": "FastAPI not installed", "status": "warning"}'
        else:
            self.send_response(404)
            response = b'{"error": "Not found"}'
        
        self.wfile.write(response)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            response = {
                "ok": True,
                "message": "Webhook received",
                "type": data.get("message", {}).get("type", "unknown"),
                "framework": "BaseHTTPRequestHandler"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except:
            self.wfile.write(b'{"ok": true}')