# Directory Structure:
# .
# ├── agents/
# │   ├── companion_agent.py
# │   ├── adaptive_questionnaire_agent.py
# │   ├── trend_monitoring_agent.py
# ├── instructions/
# │   ├── companion_instructions.txt
# │   ├── adaptive_questionnaire_instructions.txt
# │   ├── trend_monitoring_instructions.txt
# ├── data/
# │   └── synthetic_patients.json
# ├── main.py
# ├── adk.yaml
# ├── requirements.txt

# agents/companion_agent.py
from utils.helpers import load_instructions

class CompanionAgent:
    def __init__(self):
        self.instructions = load_instructions("instructions/companion_instructions.txt")

    def run(self, patient_input):
        # Stub logic (replace with actual LLM call + memory)
        return {
            "agent_response": "Hi there! It's good to check in with you. How are you feeling today?",
            "detected_emotional_state": "neutral",
            "transition_to_adaptive": True,
            "pro_intro_statement": "If you're comfortable, I have a few questions about how you’ve been feeling that might help your care team."
        }

# agents/adaptive_questionnaire_agent.py
class AdaptiveQuestionnaireAgent:
    def __init__(self):
        self.instructions = load_instructions("instructions/adaptive_questionnaire_instructions.txt")

    def run(self, patient_input):
        # Stub logic (replace with context-aware logic)
        return {
            "agent_question": "On a scale from 0 to 10, how much pain have you felt in the past 24 hours?",
            "detected_emotional_state": "neutral",
            "pro_data_extracted": {"pain_level": 6}
        }

# agents/trend_monitoring_agent.py
class TrendMonitoringAgent:
    def __init__(self):
        self.instructions = load_instructions("instructions/trend_monitoring_instructions.txt")

    def run(self, pro_data):
        risk_flag = pro_data.get("pain_level", 0) > 5
        return {
            "summary": "Patient experiencing moderate pain. Monitor for escalation.",
            "alerts": ["Pain level exceeds threshold"] if risk_flag else []
        }

# utils/helpers.py

def load_instructions(path):
    with open(path, "r") as file:
        return file.read()

# main.py (FastAPI layer)
from fastapi import FastAPI, Depends
from agents.companion_agent import CompanionAgent
from agents.adaptive_questionnaire_agent import AdaptiveQuestionnaireAgent
from agents.trend_monitoring_agent import TrendMonitoringAgent

app = FastAPI()

@app.post("/companion")
def companion_endpoint(input: dict):
    return CompanionAgent().run(input)

@app.post("/questionnaire")
def questionnaire_endpoint(input: dict):
    return AdaptiveQuestionnaireAgent().run(input)

@app.post("/trend")
def trend_endpoint(input: dict):
    return TrendMonitoringAgent().run(input)

# instructions/companion_instructions.txt
"""
You are the Companion Agent, a friendly and empathetic AI assistant...
(omitted for brevity — full text matches prior content)
"""

# instructions/adaptive_questionnaire_instructions.txt
"""
You are the Adaptive Questionnaire Agent. Your role is to conduct a personalized...
(omitted for brevity)
"""

# instructions/trend_monitoring_instructions.txt
"""
You are the Trend Monitoring Agent. Your job is to analyze structured PRO data and detect patterns...
"""

# data/synthetic_patients.json
[
  {"patient_id": 1, "name": "Alex", "history": ["mild fatigue", "pain level 3"]},
  {"patient_id": 2, "name": "Samira", "history": ["high pain", "sad"]}
]

# requirements.txt
fastapi==0.110.0
uvicorn==0.27.1
SQLAlchemy==2.0.29
psycopg2-binary==2.9.9
python-dotenv
python-multipart
pydantic==2.6.4

# adk.yaml
name: healthcare-pro-agents
entrypoint: main.py
agents:
  - agents.companion_agent.CompanionAgent
  - agents.adaptive_questionnaire_agent.AdaptiveQuestionnaireAgent
  - agents.trend_monitoring_agent.TrendMonitoringAgent
