
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def _add_cors_headers(response: JSONResponse, request: Request) -> JSONResponse:
	"""
	Inject CORS headers manually onto error responses.
	FastAPI exception handlers run outside the middleware stack, so
	CORSMiddleware never gets a chance to add these headers.
	"""
	origin = request.headers.get("origin", "*")
	response.headers["Access-Control-Allow-Origin"] = origin
	response.headers["Access-Control-Allow-Credentials"] = "true"
	response.headers["Access-Control-Allow-Methods"] = "*"
	response.headers["Access-Control-Allow-Headers"] = "*"
	return response


def setup_error_handlers(app):
	@app.exception_handler(StarletteHTTPException)
	async def http_exception_handler(request: Request, exc: StarletteHTTPException):
		response = JSONResponse(
			status_code=exc.status_code,
			content={"detail": exc.detail or "Erreur HTTP"}
		)
		return _add_cors_headers(response, request)

	@app.exception_handler(RequestValidationError)
	async def validation_exception_handler(request: Request, exc: RequestValidationError):
		# Convertir les erreurs en format sérialisable
		errors = []
		for error in exc.errors():
			error_dict = {}
			for key, value in error.items():
				# Convertir bytes en string si nécessaire
				if isinstance(value, bytes):
					error_dict[key] = value.decode('utf-8', errors='replace')
				else:
					error_dict[key] = value
			errors.append(error_dict)

		response = JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			content={"detail": errors}
		)
		return _add_cors_headers(response, request)

	@app.exception_handler(Exception)
	async def generic_exception_handler(request: Request, exc: Exception):
		response = JSONResponse(
			status_code=500,
			content={"detail": "Erreur interne du serveur"}
		)
		return _add_cors_headers(response, request)
