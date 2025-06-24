from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

class PatientRequest(BaseModel):
    patient_id: str

@app.post("/get_pro_history")
def get_pro_history(request: PatientRequest):
    with open("synthetic_data/patient_data.json") as f:
        data = json.load(f)
    if data["patient_id"] == request.patient_id:
        return {"status": "success", "data": data["pro_history"]}
    else:
        return {"status": "not found", "data": []}
