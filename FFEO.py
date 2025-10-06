"""
FFEO.py - A minimal Flask-like web framework from scratch
"""

import re
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Callable, Dict, Any, Optional


class TemplateEngine:
    """Simple template engine supporting Jinja2-like syntax"""
    
    @staticmethod
    def render(template_content: str, **context) -> str:
        """Render template with context variables"""
        result = template_content
        
        # Replace {{ variable }} with actual values
        for key, value in context.items():
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            result = re.sub(pattern, str(value), result)
        
        # Handle simple if statements: {% if variable %}...{% endif %}
        if_pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            return content if context.get(var_name) else ''
        result = re.sub(if_pattern, replace_if, result, flags=re.DOTALL)
        
        # Handle for loops: {% for item in items %}...{% endfor %}
        for_pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        def replace_for(match):
            item_name = match.group(1)
            list_name = match.group(2)
            content = match.group(3)
            items = context.get(list_name, [])
            return ''.join(content.replace('{{ ' + item_name + ' }}', str(item)) for item in items)
        result = re.sub(for_pattern, replace_for, result, flags=re.DOTALL)
        
        return result


def render_template(template_name: str, **context) -> str:
    """Load and render a template file"""
    # Look for templates in 'templates' directory
    template_path = os.path.join('templates', template_name)
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        return TemplateEngine.render(template_content, **context)
    except FileNotFoundError:
        return f"<h1>Template not found: {template_name}</h1>"


class Route:
    """Represents a route with its handler and methods"""
    
    def __init__(self, path: str, handler: Callable, methods: list):
        self.path = path
        self.handler = handler
        self.methods = methods
        self.pattern = self._create_pattern(path)
    
    def _create_pattern(self, path: str):
        """Convert Flask-style path to regex pattern"""
        # Convert <variable> to named groups
        pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', path)
        return re.compile(f'^{pattern}$')
    
    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Check if path matches this route and extract variables"""
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None


class Request:
    """Represents an HTTP request"""
    
    def __init__(self, method: str, path: str, headers: dict, body: str = ''):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.args = {}
        self.form = {}
        self._parse_query_string()
    
    def _parse_query_string(self):
        """Parse query string from URL"""
        parsed = urlparse(self.path)
        self.args = {k: v[0] if len(v) == 1 else v 
                     for k, v in parse_qs(parsed.query).items()}


class Response:
    """Represents an HTTP response"""
    
    def __init__(self, body: str = '', status: int = 200, headers: dict = None):
        self.body = body
        self.status = status
        self.headers = headers or {'Content-Type': 'text/html; charset=utf-8'}


class Feo:
    """Main application class - Flask-like interface"""
    
    def __init__(self, name: str):
        self.name = name
        self.routes: list[Route] = []
        self.error_handlers = {}
    
    def route(self, path: str, methods: list = None):
        """Decorator to register a route"""
        if methods is None:
            methods = ['GET']
        
        def decorator(func: Callable):
            self.routes.append(Route(path, func, methods))
            return func
        
        return decorator
    
    def errorhandler(self, code: int):
        """Decorator to register error handlers"""
        def decorator(func: Callable):
            self.error_handlers[code] = func
            return func
        return decorator
    
    def _find_route(self, path: str, method: str):
        """Find matching route for given path and method"""
        for route in self.routes:
            if method in route.methods:
                params = route.match(path)
                if params is not None:
                    return route, params
        return None, None
    
    def _handle_request(self, request: Request) -> Response:
        """Process request and return response"""
        parsed_url = urlparse(request.path)
        path = parsed_url.path
        
        route, params = self._find_route(path, request.method)
        
        if route:
            try:
                # Call handler with extracted parameters
                result = route.handler(**params) if params else route.handler()
                
                if isinstance(result, Response):
                    return result
                else:
                    return Response(body=str(result))
            except Exception as e:
                return Response(
                    body=f"<h1>500 Internal Server Error</h1><p>{str(e)}</p>",
                    status=500
                )
        else:
            # 404 Not Found
            if 404 in self.error_handlers:
                body = self.error_handlers[404]()
            else:
                body = f"<h1>404 Not Found</h1><p>The requested URL {path} was not found.</p>"
            return Response(body=body, status=404)
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """Start the development server"""
        app = self
        
        class FeoRequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                if debug:
                    super().log_message(format, *args)
            
            def do_GET(self):
                self._handle_request('GET')
            
            def do_POST(self):
                self._handle_request('POST')
            
            def do_PUT(self):
                self._handle_request('PUT')
            
            def do_DELETE(self):
                self._handle_request('DELETE')
            
            def _handle_request(self, method):
                # Read body for POST/PUT requests
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
                
                # Create request object
                request = Request(
                    method=method,
                    path=self.path,
                    headers=dict(self.headers),
                    body=body
                )
                
                # Process request
                response = app._handle_request(request)
                
                # Send response
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.body.encode('utf-8'))
        
        server = HTTPServer((host, port), FeoRequestHandler)
        print(f" * Running on http://{host}:{port}")
        print(f" * Debug mode: {'on' if debug else 'off'}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n * Shutting down server...")
            server.shutdown()
