from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import query

app = FastAPI(title="API Genie")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# mount catalog routes
app.include_router(query.router, prefix="/query", tags=["query"])