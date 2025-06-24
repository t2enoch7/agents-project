import json
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "mock_patient_data.json")


@app.post("/lookup_patient_data")
async def lookup_patient_data(request: Request):
    try:
        req_json = await request.json()
        patient_id = req_json.get("patient_id")

        if not patient_id:
            raise HTTPException(status_code=400, detail="Missing 'patient_id' in request body.")

        with open(DATA_FILE, "r") as f:
            all_data = json.load(f)

        patient_data = all_data.get(patient_id)

        if not patient_data:
            raise HTTPException(status_code=404, detail="Patient not found.")

        return JSONResponse(content=patient_data)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
