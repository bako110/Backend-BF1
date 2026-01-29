
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
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			content={"detail": exc.errors()}
		)

	@app.exception_handler(Exception)
	async def generic_exception_handler(request: Request, exc: Exception):
		return JSONResponse(
			status_code=500,
			content={"detail": "Erreur interne du serveur"}
		)
