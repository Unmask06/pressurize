from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import routes

app = FastAPI(title="Pressurize API", version="0.1.0")

# Allow CORS for Vue frontend (assuming runs on port 5173 by default)
origins: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Pressurize API is running"}
