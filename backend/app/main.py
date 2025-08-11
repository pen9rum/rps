from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1.routes_simulate import router as simulate_router
from .api.v1.routes_observer import router as observer_router
from .api.v1.routes_player import router as player_router
from .api.v1.routes_eval import router as eval_router

app = FastAPI(title="RPS Belief API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(simulate_router, prefix=settings.API_PREFIX)
app.include_router(observer_router, prefix=settings.API_PREFIX)
app.include_router(player_router, prefix=settings.API_PREFIX)
app.include_router(eval_router, prefix=settings.API_PREFIX)
