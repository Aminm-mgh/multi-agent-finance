import time
import json
import os
from src.graph.workflow import run_analysis
from src.agents.analyst import AnalystAgent
from src.schemas.agent_state import AgentState


def run_single_agent(ticker: str) -> dict:
    """Baseline: just the Analyst agent, no RAG, no Critic."""
    start = time.time()
    
    agent = AnalystAgent()
    state = AgentState(ticker=ticker)
    result = agent.run(state)
    
    return {
        "mode": "single_agent",
        "ticker": ticker,
        "analyst_summary": result.analyst_summary,
        "confidence_score": 0.0,
        "errors": result.errors,
        "latency_ms": (time.time() - start) * 1000
    }


def run_full_pipeline(ticker: str) -> dict:
    """Full 4-agent pipeline with RAG."""
    start = time.time()
    
    result = run_analysis(ticker)
    
    return {
        "mode": "full_pipeline",
        "ticker": ticker,
        "analyst_summary": result['analyst_summary'],
        "confidence_score": result['confidence_score'],
        "critique_summary": result['critique_summary'],
        "errors": result['errors'],
        "latency_ms": (time.time() - start) * 1000,
        "chunks_retrieved": result['total_chunks_retrieved']
    }


def run_ablation(ticker: str = "AAPL"):
    print(f"\n=== ABLATION STUDY: {ticker} ===\n")
    
    # Run single agent
    print("Running single agent baseline...")
    single = run_single_agent(ticker)
    print(f"Latency: {single['latency_ms']:.0f}ms")
    print(f"Summary: {single['analyst_summary']}")
    print(f"Errors: {single['errors']}")
    
    print("\n---\n")
    
    # Run full pipeline
    print("Running full 4-agent pipeline...")
    full = run_full_pipeline(ticker)
    print(f"Latency: {full['latency_ms']:.0f}ms")
    print(f"Summary: {full['analyst_summary']}")
    print(f"Confidence: {full['confidence_score']}")
    print(f"Chunks retrieved: {full['chunks_retrieved']}")
    print(f"Errors: {full['errors']}")
    
    print("\n=== COMPARISON ===")
    print(f"Latency increase: {full['latency_ms'] / single['latency_ms']:.1f}x slower")
    print(f"Confidence with full pipeline: {full['confidence_score']:.0%}")
    print(f"RAG chunks grounding the analysis: {full['chunks_retrieved']}")
    
    # Save results
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/ablation_{ticker}.json", "w") as f:
        json.dump({"single": single, "full": full}, f, indent=2, default=str)
    
    print(f"\nResults saved to reports/ablation_{ticker}.json")


if __name__ == "__main__":
    run_ablation("AAPL")