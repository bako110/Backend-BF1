from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
	allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
	app.add_middleware(
		CORSMiddleware,
		allow_origins=allowed_origins,
		allow_credentials=True,
		allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
		allow_headers=["Authorization", "Content-Type"],
	)
