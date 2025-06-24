from google.adk.agents import SequentialAgent
from sub_agents.companion_agent import companion_agent
from sub_agents.adaptive_questionnaire_agent import adaptive_questionnaire_agent
from sub_agents.trend_monitoring_agent import trend_monitoring_agent

pros_pipeline = SequentialAgent(
    name="PROsPipeline",
    description="Collects check-in data, adapts questionnaires, and analyzes health trends.",
    sub_agents=[
        companion_agent,
        adaptive_questionnaire_agent,
        trend_monitoring_agent
    ]
)
