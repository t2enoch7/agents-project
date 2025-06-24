from google.adk.agents import LlmAgent

def get_adaptive_questionnaire_agent():
    return LlmAgent(
        name="AdaptiveQuestionnaireAgent",
        instruction=(
            "Based on the patient's emotion from state['emotion'], generate 3 personalized follow-up questions "
            "to assess their current condition in more detail. Save to state['adaptive_questions']."
        ),
        output_key="adaptive_questions"
    )