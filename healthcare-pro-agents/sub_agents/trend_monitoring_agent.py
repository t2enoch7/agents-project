from google.adk.agents import LlmAgent
from google.adk.tools import MathTool, TableGenerationTool

math_tool = MathTool()
table_tool = TableGenerationTool()

def get_trend_monitoring_agent():
    return LlmAgent(
        name="TrendMonitoringAgent",
        tools=[math_tool, table_tool],
        instruction="""
        Examine state['pro_history'] for trends over time.
        Compare recent responses in state['adaptive_questions'].
        Highlight worsening patterns in mood, pain, or sleep.
        Provide summary and if applicable, write alert in state['alerts'].
        """,
        output_key="clinical_summary",
    )
