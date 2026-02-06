from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=False,
		allow_methods=["*"],
		allow_headers=["*"],
		expose_headers=["*"],
		max_age=600,
	)
