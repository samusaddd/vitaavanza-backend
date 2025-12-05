import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import Base, engine
from app.api.v1 import api_router

settings = get_settings()
logger = get_logger("main")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

# <<< CORS – copy this EXACT block >>>
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow ALL origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# <<< END CORS >>>

@app.middleware("http")
async def add_request_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}ms")
    return response

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
