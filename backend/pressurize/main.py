"""Pressurize API - FastAPI application for vessel pressurization simulation."""

import os
from importlib.metadata import version

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pressurize.api import routes

app = FastAPI(title="Pressurize API", version=version("pressurize"))

# Allow CORS for Vue frontend (assuming runs on port 5173 by default)
origins: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://xergiz.com",
    "https://www.xergiz.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# When running standalone (local dev), add /pressurize prefix to match frontend expectations.
# In production, the app is mounted at /pressurize by the main xergiz backend, so no prefix needed.
is_standalone = os.environ.get("PRESSURIZE_STANDALONE", "false").lower() == "true"
ROUTER_PREFIX = "/pressurize" if is_standalone else ""

app.include_router(routes.router, prefix=ROUTER_PREFIX)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint returning API status."""
    return {"message": "Pressurize API is running"}


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the Pressurize API server."""
    uvicorn.run("pressurize.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run_server()
