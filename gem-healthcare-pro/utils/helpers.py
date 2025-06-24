import json
import os

def show_state(session):
    print("\n🧾 Final Session State:")
    for k, v in session.state.items():
        print(f"{k}: {v}")

def save_session_to_file(session, user_id):
    os.makedirs("session_store", exist_ok=True)
    path = f"session_store/{user_id}_session.json"
    with open(path, "w") as f:
        json.dump(session.state, f, indent=2)
    print(f"\n💾 Session saved to {path}")
