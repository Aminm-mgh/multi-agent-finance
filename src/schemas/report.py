from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.schemas.agent_state import FinancialMetrics, NewsItem, CritiqueFlag

class FinalReport(BaseModel):
    # Identity
    run_id: str
    ticker: str
    company_name: str
    analysis_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Core outputs
    key_metrics: FinancialMetrics
    analyst_summary: str
    risk_factors: List[str]

    # News
    news_items: List[NewsItem]
    overall_news_sentiment: float
    material_news_count: int

    # Quality signals
    confidence_score: float
    critique_flags: List[CritiqueFlag]
    unresolved_flags: List[str]

    # Audit trail
    sources: List[str]
    hallucination_flags: List[str]

    # Performance
    total_latency_ms: float
    agent_latencies_ms: dict
    filing_fallback_used: bool