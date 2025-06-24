from google.adk.agents import LlmAgent

def get_trend_monitoring_agent():
    return LlmAgent(
        name="TrendMonitoringAgent",
        instruction="""
        Based on state['symptom_feedback'], detect any warning signals.
        If multiple sad or anxious entries, trigger alert in state['alerts'].
        """,
        output_key="alerts"
    )
