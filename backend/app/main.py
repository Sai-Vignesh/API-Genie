from fastapi import FastAPI
from app.routers import catalog

app = FastAPI(title="API Genie")

@app.get("/health")
def health():
    return {"ok": True}

# mount catalog routes
app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])