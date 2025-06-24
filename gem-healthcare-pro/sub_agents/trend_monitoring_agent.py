from google.adk.agents import LlmAgent

trend_monitoring_agent = LlmAgent(
    name="TrendMonitoringAgent",
    model="gemini-1.5-pro",
    instruction=(
        "Analyze historical_data from state['historical_data'] and current 'qa' to detect trends or anomalies. "
        "If risk signals are found, generate an alert and store it in state['alerts']."
    ),
    output_key="alerts"
)
