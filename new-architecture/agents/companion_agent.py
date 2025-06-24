
from typing import Dict
from agents.state_manager import get_patient_profile
from datetime import datetime

def run_companion_agent(session_state: Dict) -> Dict:
    """
    Companion Agent: Initiates check-ins and transitions to Adaptive Questionnaire Agent if ready.
    """

    user_profile = get_patient_profile(session_state.get("patient_id"))
    history = session_state.get("conversation_history", [])
    emotional_state = "neutral"

    last_input = history[-1]["user"] if history else ""
    last_bot = history[-1]["bot"] if history else ""

    if "pain" in last_input or "feeling" in last_input or "tired" in last_input:
        emotional_state = "tired"
    elif "frustrated" in last_input:
        emotional_state = "frustrated"

    transition = any(word in last_input.lower() for word in ["yes", "okay", "sure", "ready"])
    intro_text = (
        "If you're comfortable, I have a few questions about how you’ve been feeling lately."
    )

    response = {
        "agent_response": "Hi there! Just checking in — how have you been feeling today?",
        "detected_emotional_state": emotional_state,
        "transition_to_adaptive": False,
        "pro_intro_statement": ""
    }

    if transition:
        response.update({
            "agent_response": intro_text,
            "transition_to_adaptive": True,
            "pro_intro_statement": intro_text
        })

    return response
