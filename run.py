import uvicorn
from fastapi import FastAPI

from src.api import router

app = FastAPI(
    title="Freshflow sales prediction  service",
    version="0.0.1",
)
app.include_router(router)

if __name__ == "__main__":
    print("Open http://127.0.0.1:8000/docs")
    uvicorn.run("run:app",
                host="0.0.0.0",
                port=8000,
                log_level="error"
                )