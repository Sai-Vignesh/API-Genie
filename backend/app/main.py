from fastapi import FastAPI
app = FastAPI(title="API Genie")
@app.get("/health")
def health():
    return {"ok": True}
