import json
import os
import re
from src.graph.workflow import run_analysis


def extract_numerical_claims(text: str) -> list:
    patterns = [
        r'\$[\d,]+\.?\d*\s*(?:billion|million|B|M)?',
        r'[\d,]+\.?\d*\s*%',
        r'[\d,]+\.?\d+',
    ]
    claims = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        claims.extend(matches)
    return list(set(claims))


def check_claim_in_sources(claim: str, filing_chunks: list) -> bool:
    claim_clean = claim.replace('$', '').replace(',', '').replace('%', '').strip()
    for chunk in filing_chunks:
        chunk_text = chunk.get('text', '') if isinstance(chunk, dict) else str(chunk)
        if claim_clean in chunk_text:
            return True
    return False


def measure_hallucination_rate(ticker: str) -> dict:
    print(f"Running pipeline for {ticker}...")
    result = run_analysis(ticker)

    analyst_text = result['analyst_summary']
    critique_text = result['critique_summary']
    full_text = analyst_text + " " + critique_text

    claims = extract_numerical_claims(full_text)
    print(f"Found {len(claims)} numerical claims")

    filing_chunks = result.get('filing_chunks', [])
    print(f"Checking against {len(filing_chunks)} source chunks")

    grounded = 0
    ungrounded = []

    for claim in claims:
        if check_claim_in_sources(claim, filing_chunks):
            grounded += 1
        else:
            ungrounded.append(claim)

    total = len(claims)
    hallucination_rate = (total - grounded) / total if total > 0 else 0

    return {
        "ticker": ticker,
        "total_claims": total,
        "grounded_claims": grounded,
        "ungrounded_claims": ungrounded,
        "hallucination_rate": round(hallucination_rate, 3),
        "grounding_rate": round(1 - hallucination_rate, 3)
    }


if __name__ == "__main__":
    report = measure_hallucination_rate("AAPL")

    print("\n=== HALLUCINATION RATE REPORT ===")
    print(f"Ticker: {report['ticker']}")
    print(f"Total numerical claims: {report['total_claims']}")
    print(f"Grounded in source: {report['grounded_claims']}")
    print(f"Hallucination rate: {report['hallucination_rate']*100:.1f}%")
    print(f"Grounding rate: {report['grounding_rate']*100:.1f}%")
    print(f"\nUngrounded claims:")
    for c in report['ungrounded_claims'][:10]:
        print(f"  - {c}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/hallucination_rate_AAPL.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nSaved to reports/hallucination_rate_AAPL.json")