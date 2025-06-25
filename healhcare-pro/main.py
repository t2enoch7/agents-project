from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

from utils.database import DatabaseManager
from utils.companion_agent import CompanionAgent
from utils.adaptive_questionnaire_agent import AdaptiveQuestionnaireAgent
from utils.trend_monitoring_agent import TrendMonitoringAgent
from utils.auth import create_simple_token, get_current_user
from utils.models import Patient, PROResponse, ConversationSession

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Patient Reported Outcomes Multi-Agent System",
    description="A multi-agent system for collecting and analyzing patient reported outcomes using email and date of birth authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and agents
db_manager = DatabaseManager()
companion_agent = CompanionAgent()
adaptive_questionnaire_agent = AdaptiveQuestionnaireAgent()
trend_monitoring_agent = TrendMonitoringAgent()

# Pydantic models for API
class PatientCreate(BaseModel):
    email: str
    date_of_birth: str
    condition: str
    medical_history: str = ""
    preferred_language: str = "en"
    accessibility_needs: Optional[str] = None

class PatientLogin(BaseModel):
    email: str
    date_of_birth: str

class ConversationRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ConversationResponse(BaseModel):
    session_id: str
    response: str
    agent_type: str
    next_action: Optional[str] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and agents on startup"""
    await db_manager.initialize()
    logger.info("Multi-agent system initialized successfully")

# Authentication endpoints
@app.post("/auth/login")
async def login_patient(patient_data: PatientLogin):
    """Login patient using email and date of birth"""
    try:
        # Check if patient exists
        patient = await db_manager.get_patient_by_email(patient_data.email)

        if not patient:
            # Create new patient if they don't exist
            patient_id = await db_manager.create_patient(
                email=patient_data.email,
                date_of_birth=patient_data.date_of_birth,
                condition="General",  # Default condition
                medical_history=""
            )
            patient = await db_manager.get_patient(patient_id)

        # Verify date of birth
        if patient["date_of_birth"] != patient_data.date_of_birth:
            raise HTTPException(status_code=401, detail="Invalid date of birth")

        # Create token
        token = create_simple_token(patient_data.email, patient_data.date_of_birth)

        return {
            "token": token,
            "patient_id": patient["id"],
            "email": patient["email"],
            "condition": patient["condition"]
        }

    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Patient management endpoints
@app.post("/patients")
async def create_patient_profile(patient_data: PatientCreate):
    """Create or update patient profile"""
    try:
        # Check if patient exists
        existing_patient = await db_manager.get_patient_by_email(patient_data.email)

        if existing_patient:
            # Update existing patient
            await db_manager.update_medical_history(
                existing_patient["id"],
                patient_data.medical_history
            )
            patient_id = existing_patient["id"]
        else:
            # Create new patient
            patient_id = await db_manager.create_patient(
                email=patient_data.email,
                date_of_birth=patient_data.date_of_birth,
                condition=patient_data.condition,
                medical_history=patient_data.medical_history,
                preferred_language=patient_data.preferred_language,
                accessibility_needs=patient_data.accessibility_needs
            )

        return {"message": "Patient profile updated successfully", "patient_id": patient_id}

    except Exception as e:
        logger.error(f"Error creating patient profile: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}")
async def get_patient_profile(patient_id: int, token: str = Query(...)):
    """Get patient information"""
    try:
        # Verify token
        user_data = get_current_user(token)

        patient = await db_manager.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        return patient

    except Exception as e:
        logger.error(f"Error getting patient: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Multi-agent conversation endpoints
@app.post("/conversation/start")
async def start_conversation(token: str = Query(...)):
    """Start a new conversation session with the companion agent"""
    try:
        # Verify token and get patient
        user_data = get_current_user(token)
        patient = await db_manager.get_patient_by_email(user_data["email"])

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Create new session
        session_id = await db_manager.create_conversation_session(patient["id"])

        # Get initial message from companion agent
        initial_message = await companion_agent.get_initial_message(patient)

        # Store the interaction
        await db_manager.store_conversation_interaction(
            session_id=session_id,
            patient_id=patient["id"],
            message="",
            response=initial_message,
            agent_type="companion"
        )

        return {
            "session_id": session_id,
            "response": initial_message,
            "agent_type": "companion",
            "next_action": "wait_for_response"
        }

    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/continue")
async def continue_conversation(
    request: ConversationRequest,
    token: str = Query(...)
):
    """Continue conversation with adaptive agents"""
    try:
        # Verify token and get patient
        user_data = get_current_user(token)
        patient = await db_manager.get_patient_by_email(user_data["email"])

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get conversation history
        history = await db_manager.get_conversation_history(request.session_id)

        # Determine which agent should respond based on conversation flow
        if len(history) == 1:  # First response after initial greeting
            # Use companion agent to analyze emotional state and transition to questionnaire
            emotional_analysis = await companion_agent.detect_emotional_state(request.message)

            # Store the patient's response
            await db_manager.store_conversation_interaction(
                session_id=request.session_id,
                patient_id=patient["id"],
                message=request.message,
                response="",
                agent_type="patient"
            )

            # Generate adaptive questionnaire based on emotional state and medical history
            questionnaire_response = await adaptive_questionnaire_agent.process_message(
                patient=patient,
                message=request.message,
                session_id=request.session_id,
                history=history
            )

            return {
                "session_id": request.session_id,
                "response": questionnaire_response,
                "agent_type": "adaptive_questionnaire",
                "next_action": "continue_questionnaire",
                "emotional_state": emotional_analysis
            }

        else:
            # Continue with adaptive questionnaire
            response = await adaptive_questionnaire_agent.process_message(
                patient=patient,
                message=request.message,
                session_id=request.session_id,
                history=history
            )

            # Store the interaction
            await db_manager.store_conversation_interaction(
                session_id=request.session_id,
                patient_id=patient["id"],
                message=request.message,
                response=response,
                agent_type="adaptive_questionnaire"
            )

            return {
                "session_id": request.session_id,
                "response": response,
                "agent_type": "adaptive_questionnaire",
                "next_action": "continue_questionnaire"
            }

    except Exception as e:
        logger.error(f"Error continuing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/analyze")
async def analyze_trends(token: str = Query(...)):
    """Analyze patient trends and generate insights"""
    try:
        # Verify token and get patient
        user_data = get_current_user(token)
        patient = await db_manager.get_patient_by_email(user_data["email"])

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get patient's PRO data
        pro_data = await db_manager.get_patient_pro_data(patient["id"])

        # Analyze with trend monitoring agent
        analysis = await trend_monitoring_agent.analyze_patient_trends(
            patient=patient,
            pro_data=pro_data
        )

        return {
            "patient_id": patient["id"],
            "analysis": analysis,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/complete")
async def complete_conversation(session_id: str, token: str = Query(...)):
    """Complete a conversation session and generate final insights"""
    try:
        # Verify token and get patient
        user_data = get_current_user(token)
        patient = await db_manager.get_patient_by_email(user_data["email"])

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get conversation history
        history = await db_manager.get_conversation_history(session_id)

        # Generate final summary and insights
        final_insights = await trend_monitoring_agent.analyze_patient_trends(
            patient=patient,
            pro_data=await db_manager.get_patient_pro_data(patient["id"])
        )

        # Generate completion message
        completion_message = await companion_agent.generate_completion_message(
            patient=patient,
            insights=final_insights
        )

        return {
            "session_id": session_id,
            "completion_message": completion_message,
            "insights": final_insights,
            "session_summary": {
                "total_interactions": len(history),
                "session_duration": "calculated_duration",
                "key_findings": final_insights.get("recommendations", [])
            }
        }

    except Exception as e:
        logger.error(f"Error completing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "agents": {
            "companion": "active",
            "adaptive_questionnaire": "active",
            "trend_monitoring": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
