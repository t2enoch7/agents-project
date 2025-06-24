from google.adk.agents import SequentialAgent
from sub_agents.companion_agent import get_companion_agent
from sub_agents.adaptive_questionnaire_agent import get_adaptive_questionnaire_agent
from sub_agents.trend_monitoring_agent import get_trend_monitoring_agent

patient_pro_pipeline = SequentialAgent(
    name="PRO_Pipeline",
    sub_agents=[
        get_companion_agent(),
        get_adaptive_questionnaire_agent(),
        get_trend_monitoring_agent()
    ]
)