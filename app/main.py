from fastapi import FastAPI
from sqlalchemy import text

from app.api.search import router as search_router
from app.db import engine

app = FastAPI(title="Airbnb Retrieval Ranking Engine")
app.include_router(search_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/health/db")
def db_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok"}