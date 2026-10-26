"""
Simple HTTP Server for NetGuard IDS Frontend
Serves static HTML/CSS/JS files with auto-browser launch
"""
import http.server
import socketserver
import os
import webbrowser
import time
import threading

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
AUTO_OPEN_BROWSER = True  # Set to False to disable auto-open

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def open_browser():
    """Open browser after a short delay to ensure server is ready"""
    time.sleep(1.5)  # Wait for server to start
    url = f"http://localhost:{PORT}/index.html"

    # Try to open in Chrome specifically, fallback to default browser
    try:
        # Windows Chrome paths
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        chrome_found = False
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
                webbrowser.get('chrome').open(url)
                chrome_found = True
                print(f"✅ Opening Chrome: {url}")
                break

        if not chrome_found:
            # Fallback to default browser
            webbrowser.open(url)
            print(f"✅ Opening default browser: {url}")
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print(f"   Please manually open: {url}")

if __name__ == "__main__":
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🌐 NetGuard IDS - Frontend Server")
        print("=" * 60)
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Dashboard: http://localhost:{PORT}/index.html")
        print("\nPress Ctrl+C to stop")
        print("=" * 60)

        # Auto-open browser in a separate thread
        if AUTO_OPEN_BROWSER:
            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n⏹️  Server stopped")
