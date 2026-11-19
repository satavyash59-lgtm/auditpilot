from pathlib import Path

from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

BASE_DIR = Path(__file__).resolve().parent

app: FastAPI = get_fast_api_app(
    agents_dir=str(BASE_DIR),
    web=True,
    host="0.0.0.0",
    port=8080,
)


@app.get("/health")
async def health():
    return {"status": "ok"}
