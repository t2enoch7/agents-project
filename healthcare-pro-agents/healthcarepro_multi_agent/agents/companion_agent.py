from google.adk.agents import LlmAgent
from google.adk.tools import TextClassificationTool

emotion_tool = TextClassificationTool(
    name="EmotionClassifier",
    categories=["happy", "sad", "anxious", "angry", "calm"]
)

def get_companion_agent():
    return LlmAgent(
        name="CompanionAgent",
        tools=[emotion_tool],
        instruction="""
        Begin the patient interaction with a friendly tone. Ask how they feel emotionally and physically.
        Use EmotionClassifier to tag their emotional state and store in state['emotion'].
        """,
        output_key="companion_checkin",
    )
