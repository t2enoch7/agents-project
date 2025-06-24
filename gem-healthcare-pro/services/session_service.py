import os
import json
import uuid

class FileSessionService:
    def __init__(self, session_dir="sessions"):
        self.session_dir = session_dir
        os.makedirs(session_dir, exist_ok=True)

    def _get_session_path(self, app_name, user_id, session_id):
        return os.path.join(self.session_dir, f"{user_id}_{session_id}.json")

    def create_session(self, app_name, user_id, state):
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "state": state
        }
        with open(self._get_session_path(app_name, user_id, session_id), "w") as f:
            json.dump(session_data, f)
        return type("Session", (), session_data)

    def get_session(self, app_name, user_id, session_id):
        path = self._get_session_path(app_name, user_id, session_id)
        with open(path, "r") as f:
            session_data = json.load(f)
        return type("Session", (), session_data)

    def update_session(self, app_name, user_id, session_id, new_state):
        path = self._get_session_path(app_name, user_id, session_id)
        with open(path, "r") as f:
            session_data = json.load(f)
        session_data["state"] = new_state
        with open(path, "w") as f:
            json.dump(session_data, f)
