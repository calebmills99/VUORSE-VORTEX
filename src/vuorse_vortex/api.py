from fastapi import FastAPI

app = FastAPI(
    title="VUORSE-VORTEX",
    description="Escape velocity toward omniscience.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "VUORSE-VORTEX",
        "message": "Slay Mode ∞ engaged",
    }

@app.get("/health")
def health():
    return {"ok": True}
