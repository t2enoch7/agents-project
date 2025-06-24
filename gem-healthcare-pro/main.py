import asyncio
import os, json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents.pipeline import pipeline
from utils.helpers import show_state, save_session_to_file

initial_state = {
    "interaction_history": [],
    "emotion": "",
    "symptom_feedback": [],
    "alerts": [],
}

async def main_async():
    app_name = "PRO_Health"
    user_id = "patient_001"

    session_service = InMemorySessionService()
    session = session_service.create_session(app_name, user_id, initial_state)
    session_id = session.id

    runner = Runner(agent=pipeline, app_name=app_name, session_service=session_service)

    print("👋 Welcome to the Patient Check-In Agent.\n(Type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        result = await runner.run(user_id=user_id, session_id=session_id, input=user_input)
        print("Agent:", result.output)

    final_session = session_service.get_session(app_name, user_id, session_id)
    show_state(final_session)
    save_session_to_file(final_session, user_id)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
