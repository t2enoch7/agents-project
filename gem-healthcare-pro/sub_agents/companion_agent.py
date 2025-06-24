from google.adk.agents import LlmAgent
from tools.sentiment_tool import SentimentAnalysisTool

def get_companion_agent():
    return LlmAgent(
        name="CompanionAgent",
        instruction="Use SentimentAnalysisAPI to detect patient's emotion.",
        tools=[SentimentAnalysisTool()],
        output_key="emotion"
    )
