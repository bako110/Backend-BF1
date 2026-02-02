from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],  # Autorise toutes les origines
		allow_credentials=True,
		allow_methods=["*"],  # Autorise toutes les méthodes
		allow_headers=["*"],  # Autorise tous les headers
	)
