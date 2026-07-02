from pydantic import BaseModel, Field
from typing import Optional, List

class RetrievedChunk(BaseModel):
    text: str
    source_document: str
    section: str
    page_number: int
    relevance_score: float

class FinancialMetrics(BaseModel):
    pe_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    gross_margin: Optional[float] = None
    current_ratio: Optional[float] = None
    eps: Optional[float] = None
    market_cap_billions: Optional[float] = None

class NewsItem(BaseModel):
    title: str
    published_at: str
    source: str
    sentiment_score: float
    summary: str
    is_material: bool

class CritiqueFlag(BaseModel):
    flag_type: str
    description: str
    severity: str
    agents_involved: List[str]


class AgentState(BaseModel):
    # Input
    ticker: str
    company_name: str = ""
    run_id: str = ""

    # Researcher output
    filing_chunks: List[RetrievedChunk] = Field(default_factory=list)
    filing_retrieval_success: bool = False

    # Analyst output
    financial_metrics: Optional[FinancialMetrics] = None
    analyst_summary: str = ""
    analyst_sources: List[str] = Field(default_factory=list)

    # News agent output
    material_news_count: int = 0
    news_items: List[NewsItem] = Field(default_factory=list)
    overall_news_sentiment: float = 0.0

    # Critic output
    confidence_score: float = 0.0
    critique_flags: List[CritiqueFlag] = Field(default_factory=list)
    critique_summary: str = ""

    # Pipeline metadata
    total_chunks_retrieved: int = 0
    errors: List[str] = Field(default_factory=list)
    agent_latencies_ms: dict = Field(default_factory=dict)