
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

class LoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		logging.info(f"{request.method} {request.url}")
		response = await call_next(request)
		return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		response = await call_next(request)
		response.headers['X-Content-Type-Options'] = 'nosniff'
		response.headers['X-Frame-Options'] = 'DENY'
		response.headers['X-XSS-Protection'] = '1; mode=block'
		return response

def setup_middlewares(app):
	app.add_middleware(LoggingMiddleware)
	app.add_middleware(SecurityHeadersMiddleware)
