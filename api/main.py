import sys
import os
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    logger.info("Root endpoint called")
    return jsonify({"message": "API is running", "status": "ok"})

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health endpoint called")
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        return jsonify({"ok": True, "message": "webhook received"})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"ok": True})

# Vercel looks for this exact variable name
handler = app