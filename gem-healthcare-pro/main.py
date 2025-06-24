import asyncio
from agents.pipeline import pros_pipeline  # Your SequentialAgent pipeline
from services.session_service import InMemorySessionService
from runners.agent_runner import Runner

# === INITIAL STATE SETUP ===
initial_state = {
    "user_name": "Brandon",
    "historical_data": [
        {"date": "2024-06-01", "symptoms": "fatigue"},
        {"date": "2024-06-05", "symptoms": "fatigue, headache"},
        {"date": "2024-06-10", "symptoms": "dizzy, fatigue"}
    ],
    "checkin": "",
    "qa": "",
    "alerts": ""
}

APP_NAME = "PROsHealthApp"
USER_ID = "brandon123"

# === SETUP SESSION SERVICE ===
session_service = InMemorySessionService()

async def main_async():
    # === CREATE SESSION ===
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state
    )
    session_id = session.id
    print(f"[✓] New session started: {session_id}")

    # === SETUP RUNNER ===
    runner = Runner(
        agent=pros_pipeline,  # The full agent pipeline
        app_name=APP_NAME,
        session_service=session_service
    )

    # === CONVERSATION LOOP ===
    print("\n[Patient Check-in System]")
    print("Type your symptom update. Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Session ended.")
            break

        # Run the pipeline with input
        result = await runner.run(
            user_id=USER_ID,
            session_id=session_id,
            input=user_input
        )

        print(f"\n[System]: {result.output}\n")

    # === FINAL STATE ===
    final = session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )

    print("\n[Final Session State]:")
    for k, v in final.state.items():
        print(f"{k}: {v}")


def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
