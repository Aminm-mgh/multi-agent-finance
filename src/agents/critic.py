import os
from anthropic import Anthropic
from src.schemas.agent_state import AgentState, CritiqueFlag
import time

from dotenv import load_dotenv
load_dotenv()


class CriticAgent:
    def __init__(self):
        self.client = Anthropic()

    def build_prompt(self, state: AgentState) -> str:
        chunks_text = "\n".join([f"- {c.text[:200]}" for c in state.filing_chunks[:5]])
        
        return f"""You are a financial research critic. Review the following analysis and identify any issues.

TICKER: {state.ticker}

FINANCIAL METRICS FROM ANALYST:
{state.analyst_summary}

TOP FILING CHUNKS FROM SEC 10-K:
{chunks_text}

NEWS SENTIMENT: {state.overall_news_sentiment}
ARTICLES REVIEWED: {len(state.news_items)}

Your job:
1. Check if the financial metrics seem consistent with the filing
2. Identify any red flags or uncertainties
3. Assign a confidence score from 0.0 to 1.0
4. List any unresolved concerns

Respond in this exact format:
CONFIDENCE: [number between 0 and 1]
FLAGS: [comma separated list of concerns, or NONE]
SUMMARY: [2-3 sentence summary of your critique]"""
    


    def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            prompt = self.build_prompt(state)
            
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text
            
            # Parse confidence score
            for line in text.split('\n'):
                if line.startswith('CONFIDENCE:'):
                    try:
                        state.confidence_score = float(line.replace('CONFIDENCE:', '').strip())
                    except:
                        state.confidence_score = 0.5
                
                elif line.startswith('FLAGS:'):
                    flags_text = line.replace('FLAGS:', '').strip()
                    if flags_text != 'NONE':
                        for flag in flags_text.split(','):
                            state.critique_flags.append(CritiqueFlag(
                                flag_type="uncertainty",
                                description=flag.strip(),
                                severity="medium",
                                agents_involved=["critic"]
                            ))
                
                elif line.startswith('SUMMARY:'):
                    state.critique_summary = line.replace('SUMMARY:', '').strip()

        except Exception as e:
            state.errors.append(f"Critic error: {str(e)}")
            state.confidence_score = 0.0

        state.agent_latencies_ms['critic'] = (time.time() - start) * 1000
        return state