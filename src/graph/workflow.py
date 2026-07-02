from langgraph.graph import StateGraph, END
from src.schemas.agent_state import AgentState
from src.agents.researcher import ResearcherAgent
from src.agents.analyst import AnalystAgent
from src.agents.news_agent import NewsAgent
from src.agents.critic import CriticAgent

def create_workflow():
    # Initialise all agents
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    news = NewsAgent()
    critic = CriticAgent()

    # Create the graph
    graph = StateGraph(AgentState)

    # Add each agent as a node
    graph.add_node("researcher", researcher.run)
    graph.add_node("analyst", analyst.run)
    graph.add_node("news", news.run)
    graph.add_node("critic", critic.run)

    # Define the flow between agents
    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "news")
    graph.add_edge("news", "critic")
    graph.add_edge("critic", END)

    return graph.compile()


def run_analysis(ticker: str, company_name: str = "") -> AgentState:
    app = create_workflow()
    
    initial_state = AgentState(
        ticker=ticker,
        company_name=company_name,
        run_id=f"{ticker}_{__import__('time').strftime('%Y%m%d_%H%M%S')}"
    )
    
    result = app.invoke(initial_state)
    return result