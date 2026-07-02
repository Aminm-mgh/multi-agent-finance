import requests
import os
from dotenv import load_dotenv
from src.schemas.agent_state import AgentState, NewsItem
import time

load_dotenv()



class NewsAgent:
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news(self, ticker: str, company_name: str = "") -> list:
        query = company_name if company_name else ticker
        
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        return data.get("articles", [])
    

    def analyse_sentiment(self, text: str) -> float:
        positive_words = ["growth", "profit", "beat", "strong", "record", "surge", "gain", "up", "rise", "positive"]
        negative_words = ["loss", "decline", "miss", "weak", "fall", "drop", "down", "risk", "concern", "lawsuit"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
            
        return (positive_count - negative_count) / total
    


    def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            articles = self.fetch_news(state.ticker, state.company_name)

            news_items = []
            sentiments = []

            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "") or ""
                content = title + " " + description

                sentiment = self.analyse_sentiment(content)
                sentiments.append(sentiment)

                news_item = NewsItem(
                    title=title,
                    published_at=article.get("publishedAt", ""),
                    source=article.get("source", {}).get("name", ""),
                    sentiment_score=sentiment,
                    summary=description[:200] if description else "",
                    is_material=False
                )
                news_items.append(news_item)

            state.news_items = news_items
            state.overall_news_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            state.material_news_count = len(news_items)

        except Exception as e:
            state.errors.append(f"News agent error: {str(e)}")

        state.agent_latencies_ms['news'] = (time.time() - start) * 1000
        return state