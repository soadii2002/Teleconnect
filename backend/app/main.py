from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import user, token, plan
from app.api.auth import router as auth_router
from app.api.plans import router as plans_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TeleConnect API")

app.include_router(auth_router)
app.include_router(plans_router)

@app.get("/")
def health_check():
    return {"status": "TeleConnect API is running"}