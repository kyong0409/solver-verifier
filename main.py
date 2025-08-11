from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from solver_verifier.api.pipeline_router import router as pipeline_router

app = FastAPI(
    title="RFP Business Requirements Extractor",
    description="A 6-stage Analyzer-Verifier pipeline for extracting business requirements from RFP documents",
    version="0.1.0"
)

# Include routers
app.include_router(pipeline_router)

# Serve static files (React frontend)
frontend_dist = Path("frontend/build")
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist / "static")), name="static")
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

@app.get("/api")
async def api_root():
    return {
        "message": "RFP Business Requirements Extractor API",
        "description": "6-stage Analyzer-Verifier pipeline for requirement extraction",
        "version": "0.1.0",
        "pipeline_stages": 6,
        "endpoints": {
            "process": "/pipeline/process",
            "status": "/pipeline/status/{set_id}",
            "configure": "/pipeline/configure",
            "stages_info": "/pipeline/stages"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rfp-requirement-extractor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
