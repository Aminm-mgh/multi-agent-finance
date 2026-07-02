import yfinance as yf
from src.schemas.agent_state import AgentState, FinancialMetrics
import time


class AnalystAgent:
    def __init__(self):
        pass

    def fetch_metrics(self, ticker: str) -> FinancialMetrics:
        stock = yf.Ticker(ticker)
        info = stock.info

        return FinancialMetrics(
            pe_ratio=info.get('trailingPE'),
            debt_to_equity=info.get('debtToEquity'),
            revenue_growth_yoy=info.get('revenueGrowth'),
            gross_margin=info.get('grossMargins'),
            current_ratio=info.get('currentRatio'),
            eps=info.get('trailingEps'),
            market_cap_billions=info.get('marketCap', 0) / 1e9 if info.get('marketCap') else None
        )
    

    def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            # Fetch live metrics from Yahoo Finance
            metrics = self.fetch_metrics(state.ticker)
            state.financial_metrics = metrics

            # Summarise what we found
            summary_parts = []
            if metrics.pe_ratio:
                summary_parts.append(f"P/E ratio: {metrics.pe_ratio:.2f}")
            if metrics.debt_to_equity:
                summary_parts.append(f"Debt/Equity: {metrics.debt_to_equity:.2f}")
            if metrics.revenue_growth_yoy:
                summary_parts.append(f"Revenue growth YoY: {metrics.revenue_growth_yoy*100:.1f}%")
            if metrics.gross_margin:
                summary_parts.append(f"Gross margin: {metrics.gross_margin*100:.1f}%")
            if metrics.market_cap_billions:
                summary_parts.append(f"Market cap: ${metrics.market_cap_billions:.1f}B")

            state.analyst_summary = " | ".join(summary_parts)
            state.analyst_sources.append("Yahoo Finance (yfinance)")

        except Exception as e:
            state.errors.append(f"Analyst error: {str(e)}")

        state.agent_latencies_ms['analyst'] = (time.time() - start) * 1000
        return state