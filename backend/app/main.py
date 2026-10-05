from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import Base,engine,SessionLocal
from app.db.seed import seed_database
from app.api.router import api
from app.core.config import settings
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    db=SessionLocal()
    try:
        seed_database(db)
        db.commit()
    finally:
        db.close()
    yield

app=FastAPI(title="Hotel Management API",version="1.0.0",openapi_url="/api/v1/openapi.json",docs_url="/api/docs",lifespan=lifespan)
local_frontend_origins = {settings.frontend_url.rstrip("/"), "http://localhost:3000", "http://127.0.0.1:3000"}
app.add_middleware(CORSMiddleware,allow_origins=sorted(local_frontend_origins),allow_credentials=False,allow_methods=["*"],allow_headers=["*"])
app.include_router(api,prefix="/api/v1")
@app.get('/health')
def health(): return {"status":"ok"}

@app.get('/')
def root():
    return {"status": "ok", "docs": "/api/docs", "api": "/api/v1"}
