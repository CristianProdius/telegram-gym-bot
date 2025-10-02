#!/usr/bin/env python3
"""
Simple webhook server for automatic deployment
Listens for GitHub webhook events and triggers deployment
"""

import os
import json
import hmac
import hashlib
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')
DEPLOY_SCRIPT = '/home/deploy/telegram-gym-bot/scripts/deploy.sh'
PORT = 9001

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/webhook-deploy':
            self.send_response(404)
            self.end_headers()
            return

        # Read the payload
        content_length = int(self.headers.get('Content-Length', 0))
        payload_body = self.rfile.read(content_length)

        # Verify signature if secret is configured
        if WEBHOOK_SECRET != 'your-webhook-secret-here':
            signature = self.headers.get('X-Hub-Signature-256')
            if not self.verify_signature(payload_body, signature):
                self.send_response(401)
                self.end_headers()
                return

        # Parse JSON
        try:
            payload = json.loads(payload_body.decode('utf-8'))
        except:
            self.send_response(400)
            self.end_headers()
            return

        # Check if it's a push to main branch
        if payload.get('ref') == 'refs/heads/main':
            print(f"[WEBHOOK] Received push to main from {payload.get('pusher', {}).get('name', 'unknown')}")
            print(f"[WEBHOOK] Commit: {payload.get('head_commit', {}).get('message', 'No message')}")

            # Trigger deployment
            self.deploy()

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")

    def verify_signature(self, payload_body, signature_header):
        """Verify that the payload was sent from GitHub by validating SHA256 signature"""
        if not signature_header:
            return False

        hash_object = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            msg=payload_body,
            digestmod=hashlib.sha256
        )
        expected_signature = "sha256=" + hash_object.hexdigest()

        return hmac.compare_digest(expected_signature, signature_header)

    def deploy(self):
        """Execute deployment script"""
        print("[WEBHOOK] Starting deployment...")
        try:
            result = subprocess.run(
                ['/bin/bash', DEPLOY_SCRIPT],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                print("[WEBHOOK] Deployment successful!")
                print(result.stdout)
            else:
                print("[WEBHOOK] Deployment failed!")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("[WEBHOOK] Deployment timeout!")
        except Exception as e:
            print(f"[WEBHOOK] Deployment error: {e}")

    def log_message(self, format, *args):
        """Suppress default logging"""
        return

if __name__ == '__main__':
    print(f"Starting webhook server on port {PORT}...")
    print(f"Webhook URL: http://your-server:9001/webhook-deploy")
    print("Add this URL to GitHub repository settings -> Webhooks")

    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down webhook server...")
        server.shutdown()