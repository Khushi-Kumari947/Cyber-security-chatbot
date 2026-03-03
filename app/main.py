from fastapi import FastAPI
from contextlib import asynccontextmanager
from .s3_loader import load_assets
from .engine import CyberSearchEngine

# Global placeholder for the engine
engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    print("Startup: Syncing assets from S3...")
    load_assets() # This is your s3_loader.py logic
    
    print("Startup: Loading Search Engine...")
    engine = CyberSearchEngine()
    yield
    # Cleanup on shutdown
    del engine

app = FastAPI(lifespan=lifespan)

@app.get("/")
def health():
    return {"status": "ready", "capacity": "76k_records"}

@app.get("/ask")
async def ask_question(q: str):
    if not q:
        return {"error": "No query provided"}
    
    answer = engine.search(q)
    return {"question": q, "answer": answer}