from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Basic routing
    if request.method == 'GET':
        if path == 'health' or request.path == '/health':
            return {'status': 'healthy'}
        elif path == '':
            return {'message': 'API is running', 'status': 'ok'}
    
    return {'error': 'Not found'}, 404

# ⚠️ CRITICAL: Export the Flask app directly for Vercel
# Vercel will automatically wrap it
application = app