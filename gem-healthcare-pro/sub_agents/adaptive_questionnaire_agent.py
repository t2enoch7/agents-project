from google.adk.agents import LlmAgent

adaptive_questionnaire_agent = LlmAgent(
    name="AdaptiveQuestionnaireAgent",
    model="gemini-1.5-pro",
    instruction=(
        "Based on the user's check-in in state['checkin'], ask follow-up questions. "
        "Adapt tone and complexity to the patient's language. "
        "Store the responses in state['qa']."
    ),
    output_key="qa"
)
