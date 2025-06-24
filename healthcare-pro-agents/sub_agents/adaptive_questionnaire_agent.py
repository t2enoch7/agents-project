from google.adk.agents import LlmAgent
from google.adk.tools import TextRewritingTool

rewriting_tool = TextRewritingTool(name="ToneAdapter")

def get_adaptive_questionnaire_agent():
    return LlmAgent(
        name="AdaptiveQuestionnaireAgent",
        tools=[rewriting_tool],
        instruction="""
        Generate 3-5 health questions adapted to the emotional state stored in state['emotion'].
        Rewrite them for clarity and tone using ToneAdapter.
        Store in state['adaptive_questions'].
        """,
        output_key="adaptive_questions",
    )
