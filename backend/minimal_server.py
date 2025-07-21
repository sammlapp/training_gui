#!/usr/bin/env python3
"""Minimal HTTP server for testing PyInstaller + Electron packaging."""

import sys
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "Minimal server running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_server(port=8000):
    """Start the minimal HTTP server."""
    server = HTTPServer(('localhost', port), SimpleHandler)
    print(f"Minimal server starting on port {port}")
    
    # Run in a separate thread so we can handle shutdown
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        server_thread.join()

def main():
    parser = argparse.ArgumentParser(description='Minimal test server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    parser.add_argument('--test', action='store_true', help='Run quick test and exit')
    
    args = parser.parse_args()
    
    if args.test:
        print("✅ Minimal server test successful!")
        print(f"Python version: {sys.version}")
        print(f"PyInstaller bundling: {'✅ SUCCESS' if getattr(sys, 'frozen', False) else '❌ Not bundled'}")
        return 0
    
    start_server(args.port)
    return 0

if __name__ == "__main__":
    sys.exit(main())