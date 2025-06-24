from google.adk.tools import Tool

class SentimentAnalysisTool(Tool):
    name = "SentimentAnalysisAPI"

    def run(self, input_text: str) -> str:
        if "tired" in input_text or "sad" in input_text:
            return "sad"
        elif "happy" in input_text:
            return "happy"
        elif "angry" in input_text:
            return "angry"
        elif "anxious" in input_text:
            return "anxious"
        else:
            return "neutral"
