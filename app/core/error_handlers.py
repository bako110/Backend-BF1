
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

def setup_error_handlers(app):
	@app.exception_handler(StarletteHTTPException)
	async def http_exception_handler(request: Request, exc: StarletteHTTPException):
		return JSONResponse(
			status_code=exc.status_code,
			content={"detail": exc.detail or "Erreur HTTP"}
		)

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
		
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			content={"detail": errors}
		)

	@app.exception_handler(Exception)
	async def generic_exception_handler(request: Request, exc: Exception):
		return JSONResponse(
			status_code=500,
			content={"detail": "Erreur interne du serveur"}
		)
