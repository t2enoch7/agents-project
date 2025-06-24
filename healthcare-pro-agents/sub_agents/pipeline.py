from google.adk.agents import SequentialAgent
from subagents.companion_agent import get_companion_agent
from subagents.adaptive_questionnaire_agent import get_adaptive_questionnaire_agent
from subagents.trend_monitoring_agent import get_trend_monitoring_agent

pro_pipeline = SequentialAgent(
    name="PRO_Pipeline",
    sub_agents=[
        get_companion_agent(),
        get_adaptive_questionnaire_agent(),
        get_trend_monitoring_agent()
    ]
)
