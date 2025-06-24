from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Patient, PROEntry, ConsentLog
from agents.companion_agent import run_companion_agent
from agents.adaptive_questionnaire_agent import run_adaptive_agent
from agents.trend_monitor_agent import analyze_trends
from utils.persistence import save_pro_data
from utils.alerts import get_latest_alerts
from datetime import datetime

router = APIRouter()

@router.post("/start-checkin/")
async def start_checkin(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    session_state = {"patient_id": patient.id}
    result = run_companion_agent(session_state)

    return result


@router.post("/continue-questionnaire/")
async def continue_questionnaire(patient_id: int, response: dict, db: Session = Depends(get_db)):
    session_state = {
        "patient_id": patient_id,
        "last_patient_response": response
    }

    result = run_adaptive_agent(session_state)

    if result["pro_data_extracted"]:
        save_pro_data(patient_id, result["pro_data_extracted"], db, source_agent="adaptive")

    return result


@router.get("/monitor-trends/{patient_id}")
async def monitor_trends(patient_id: int, db: Session = Depends(get_db)):
    result = analyze_trends(patient_id, db)
    return result


@router.get("/pro-history/{patient_id}")
async def get_pro_history(patient_id: int, db: Session = Depends(get_db)):
    entries = db.query(PROEntry).filter(PROEntry.patient_id == patient_id).order_by(PROEntry.timestamp.desc()).all()
    return [{"data": entry.data, "timestamp": entry.timestamp.isoformat()} for entry in entries]

@router.get("/alerts/{patient_id}")
async def get_alerts(patient_id: int, db: Session = Depends(get_db)):
    return get_latest_alerts(patient_id, db)
