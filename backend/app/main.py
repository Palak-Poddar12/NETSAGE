from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="NetSage AI Backend",
    description="AI-assisted Cisco network troubleshooting backend",
    version="1.0.0",
)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173",
)

origins = [
    origin.strip()
    for origin in cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "netsage-backend",
    }
