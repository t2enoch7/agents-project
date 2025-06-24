from google.adk.agents import LlmAgent

def get_trend_monitoring_agent():
    return LlmAgent(
        name="TrendMonitoringAgent",
        instruction=(
            "Analyze state['adaptive_questions'] and emotional state from state['emotion']. "
            "Compare with historical data in state['pro_history']. Identify any concerning trends and "
            "write a clinical summary to state['clinical_summary'] and any alerts to state['alerts']."
        )
    )