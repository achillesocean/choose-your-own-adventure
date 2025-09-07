from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from routers.job import router as job_router
from routers.story import router as story_router

app = FastAPI(
  title="Choose Your Own Adventure Game API",
  description="generate stories using LLMs",
  version="0.1.0",
  docs_url="/docs",
  redoc_url="/redoc"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.ALLOWED_ORIGINS,
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True
)

app.include_router(story_router, prefix=settings.API_PREFIX)
app.include_router(job_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
  