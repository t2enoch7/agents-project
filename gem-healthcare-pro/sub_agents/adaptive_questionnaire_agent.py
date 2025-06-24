from google.adk.agents import LlmAgent

def get_questionnaire_agent():
    return LlmAgent(
        name="AdaptiveQuestionnaireAgent",
        instruction="""
        Use emotion from state['emotion'] to generate 1 follow-up question.
        If sad, ask about sleep. If happy, ask what’s going well.
        """,
        output_key="symptom_feedback"
    )
