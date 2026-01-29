"""
Simple HTTP Server for Frontend
Run: python server.py
Then open: http://localhost:8000
"""
import http.server
import socketserver
import os
import webbrowser
from time import sleep

PORT = 8000
HANDLER = http.server.SimpleHTTPRequestHandler

# Change to frontend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), HANDLER) as httpd:
    print(f"🌐 Frontend Server Started!")
    print(f"📍 Open: http://localhost:{PORT}")
    print(f"🔌 Backend should be running on: http://localhost:5000")
    print(f"⏹️  Press CTRL+C to stop")
    
    # Try to open browser automatically
    try:
        sleep(1)
        webbrowser.open(f"http://localhost:{PORT}")
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
