from google.adk.agents import LlmAgent

def get_companion_agent():
    return LlmAgent(
        name="CompanionAgent",
        instruction="Conduct a friendly emotional check-in with the patient. Capture their current wellbeing and emotional tone.",
        output_key="emotion",
    )