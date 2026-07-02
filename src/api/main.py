from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import json
import os
from src.graph.workflow import run_analysis

app = FastAPI(title="Multi-Agent Financial Research System")

class AnalysisRequest(BaseModel):
    ticker: str
    company_name: str = ""

os.makedirs("reports", exist_ok=True)

@app.post("/analyse")
def analyse(request: AnalysisRequest):
    try:
        result = run_analysis(request.ticker, request.company_name)
        
        # Save report to disk
        run_id = result['run_id']
        report_path = f"reports/{run_id}.json"
        
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        return {
            "run_id": run_id,
            "ticker": result['ticker'],
            "analyst_summary": result['analyst_summary'],
            "confidence_score": result['confidence_score'],
            "critique_summary": result['critique_summary'],
            "news_sentiment": result['overall_news_sentiment'],
            "errors": result['errors']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@app.get("/report/{run_id}")
def get_report(run_id: str):
    report_path = f"reports/{run_id}.json"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    return report


@app.get("/health")
def health():
    return {"status": "ok"}