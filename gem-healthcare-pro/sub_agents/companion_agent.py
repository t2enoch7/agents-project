from google.adk.agents import LlmAgent

companion_agent = LlmAgent(
    name="CompanionAgent",
    model="gemini-1.5-pro",
    instruction="Initiate a friendly patient check-in. Ask how they are feeling today.",
    output_key="checkin"
)
