from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from agents.checklist_agent import generate_checklist

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    company_data: Dict[str, Any]
    rfp_summary: str

@app.post("/api/analyze")
async def analyze_rfp(request: AnalysisRequest):
    try:
        result = generate_checklist({
            "company_data": request.company_data,
            "rfp_summary": request.rfp_summary
        })
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
