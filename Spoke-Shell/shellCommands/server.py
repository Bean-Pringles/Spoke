from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

def run(args):
    if len(args) < 1:
        print("Usage: server <port> [handler]")
        print("Handlers: simple")
        return
    
    try:
        PORT = int(args[0])
    except ValueError:
        print("Error: Port must be a number")
        return

    # Map string names to handler classes
    handlers = {
        "simple": SimpleHTTPRequestHandler,
    }

    if len(args) > 1:
        handler_name = args[1].lower()
        Handler = handlers.get(handler_name)
        if Handler is None:
            print(f"Unknown handler '{handler_name}', using default SimpleHTTPRequestHandler")
            Handler = SimpleHTTPRequestHandler
    else:
        Handler = SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT} with handler {Handler.__name__}")
        httpd.serve_forever()