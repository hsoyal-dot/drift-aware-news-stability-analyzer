from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from pathlib import Path

# Add project root to sys.path to import drift_analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from drift_analyzer.pipeline import run_analysis
from backend_auth import auth_router, get_current_user, User

app = FastAPI(title="Drift-Aware News Stability Analyzer API")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

class AnalyzeRequest(BaseModel):
    article: str

@app.post("/api/analyze")
async def analyze_article(request: AnalyzeRequest, current_user: User = Depends(get_current_user)):
    if not request.article.strip():
        raise HTTPException(status_code=400, detail="Article text cannot be empty.")
    try:
        config_path = str(Path(os.path.dirname(os.path.abspath(__file__))) / "drift_analyzer" / "config.yaml")
        # Run pipeline
        analysis_result = run_analysis(request.article, config_path=config_path)
        return analysis_result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend_main:app", host="127.0.0.1", port=8000, reload=True)
