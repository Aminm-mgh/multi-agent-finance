import requests
import os
from dotenv import load_dotenv
from src.retrieval.hybrid_search import HybridSearch
from src.schemas.agent_state import AgentState, RetrievedChunk
from src.retrieval.text_extractor import TextExtractor
import time as t

load_dotenv()


SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&forms=10-K"

SEC_HEADERS = {
    "User-Agent": os.getenv("SEC_USER_AGENT"),
    "Accept-Encoding": "gzip, deflate",
    "Host": "efts.sec.gov"
}



class ResearcherAgent:
    def __init__(self):
        self.hybrid_search = HybridSearch()
        self.extractor = TextExtractor()

    

    def fetch_filing(self, ticker: str) -> str:
        headers = {"User-Agent": os.getenv("SEC_USER_AGENT")}

        # Step 1: get CIK from ticker
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(tickers_url, headers=headers)
        tickers_data = response.json()

        cik = None
        for entry in tickers_data.values():
            if entry['ticker'].upper() == ticker.upper():
                cik = str(entry['cik_str']).zfill(10)
                break

        if not cik:
            return None

        # Step 2: get latest 10-K accession number
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(submissions_url, headers=headers)
        data = response.json()

        forms = data['filings']['recent']['form']
        accessions = data['filings']['recent']['accessionNumber']

        for i, form in enumerate(forms):
            if form == '10-K':
                accession = accessions[i]
                accession_nodash = accession.replace('-', '')
                cik_short = str(int(cik))
                ticker_lower = ticker.lower()
                
                # Get the filing index to find the .htm file
                index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_short}/{accession_nodash}/{accession}-index.htm"
                idx_response = requests.get(index_url, headers=headers)
                
                # Find the main htm file (ticker-date.htm pattern)
                import re
                htm_match = re.search(rf'{ticker_lower}-\d+\.htm', idx_response.text, re.IGNORECASE)
                if htm_match:
                    htm_file = htm_match.group(0)
                    return f"https://www.sec.gov/Archives/edgar/data/{cik_short}/{accession_nodash}/{htm_file}"
                
                # Fallback to txt
                return f"https://www.sec.gov/Archives/edgar/data/{cik_short}/{accession_nodash}/{accession}.txt"

        
        return None
    

    def download_filing_text(self, filing_url: str) -> str:
        headers = {"User-Agent": os.getenv("SEC_USER_AGENT")}
        response = requests.get(filing_url, headers=headers)
        
        if response.status_code != 200:
            return None
            
        return response.text


    def chunk_and_index(self, text: str, ticker: str) -> int:
        words = text.split()
        chunk_size = 512
        overlap = 50
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        metadatas = [{"source": f"{ticker}_10K", "section": "filing", "page": i+1} for i in range(len(chunks))]
        run_ts = int(t.time())
        ids = [f"{ticker}_chunk_{run_ts}_{i}" for i in range(len(chunks))]

        self.hybrid_search.add_chunks(chunks, metadatas, ids)
        return len(chunks)
    

    def run(self, state: AgentState) -> AgentState:
        import time
        start = time.time()

        try:
            # Step 1: fetch filing URL
            filing_url = self.fetch_filing(state.ticker)

            if not filing_url:
                state.errors.append(f"Researcher: could not find 10-K for {state.ticker}")
                state.filing_retrieval_success = False
                return state

            # Step 2: download the text
            text = self.download_filing_text(filing_url)

            if not text:
                state.errors.append(f"Researcher: could not download filing from {filing_url}")
                state.filing_retrieval_success = False
                return state

            # Step 3: clean text then chunk and index into RAG
            clean_text = self.extractor.extract_narrative(text)
            num_chunks = self.chunk_and_index(clean_text, state.ticker)

            # Step 4: search for the most relevant chunks
            results = self.hybrid_search.search(
                "risk factors revenue income debt financial highlights",
                n_results=10
            )

            for r in results:
                chunk = RetrievedChunk(
                    text=r['text'],
                    source_document=r['metadata']['source'],
                    section=r['metadata']['section'],
                    page_number=r['metadata']['page'],
                    relevance_score=0.9
                )
                state.filing_chunks.append(chunk)

            state.filing_retrieval_success = True

        except Exception as e:
            state.errors.append(f"Researcher error: {str(e)}")
            state.filing_retrieval_success = False

        state.agent_latencies_ms['researcher'] = (time.time() - start) * 1000
        return state