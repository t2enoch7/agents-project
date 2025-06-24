import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from subagents.pipeline import pro_pipeline
from utils.patient_data_service import fetch_pro_history

load_dotenv()

session_service = InMemorySessionService()

# === Set Patient Details ===
PATIENT_ID = "patient_jane"
USER_ID = PATIENT_ID
APP_NAME = "PRO Monitoring"

# === Load synthetic historical PROs from Cloud ===
pro_history = fetch_pro_history(PATIENT_ID)

initial_state = {
    "patient_id": PATIENT_ID,
    "pro_history": pro_history,
    "interaction_history": []
}


async def main_async():
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )

    SESSION_ID = session.id
    print(f"\n📋 Session started for {USER_ID}, session: {SESSION_ID}\n")

    runner = Runner(
        agent=pro_pipeline,
        app_name=APP_NAME,
        session_service=session_service,
    )

    while True:
        user_input = input("You (Patient): ")

        if user_input.lower() in ["exit", "quit"]:
            break

        await runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            user_query=user_input
        )

    final_session = session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
    print("\n🧠 Final Session State:")
    for k, v in final_session.state.items():
        print(f"{k}: {v}")


def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
