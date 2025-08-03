from django.utils.deprecation import MiddlewareMixin

class CustomCORSMiddleware(MiddlewareMixin):
    """Custom CORS middleware to allow all origins for open endpoints."""
    
    def process_response(self, request, response):
        # Open access endpoints that should allow all origins
        open_endpoints = ['/api/convert/', '/api/health/']
        
        if any(request.path.startswith(endpoint) for endpoint in open_endpoints):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
            
        return response