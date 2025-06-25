from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResponseType(str, Enum):
    TEXT = "text"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    SCALE = "scale"
    MULTIPLE_CHOICE = "multiple_choice"

# Base models
class Patient(BaseModel):
    id: int
    email: str
    date_of_birth: str
    condition: str
    medical_history: str = ""
    preferred_language: str = "en"
    accessibility_needs: Optional[str] = None
    created_at: datetime

class AgentResponse(BaseModel):
    response: str
    agent_type: str
    timestamp: datetime
    emotional_state: Optional[Dict[str, Any]] = None

class CheckInSchedule(BaseModel):
    patient_id: int
    frequency: str  # daily, weekly, monthly
    preferred_time: str
    active: bool = True

class PROResponse(BaseModel):
    patient_id: int
    session_id: str
    question_id: str
    response_value: str
    response_type: ResponseType
    timestamp: datetime

class ConversationSession(BaseModel):
    id: str
    patient_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # active, completed, abandoned

class TrendAnalysis(BaseModel):
    patient_id: int
    analysis_date: datetime
    trends: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    recommendations: List[str]
    risk_score: Optional[float]
    data_points: int

class TrendAlert(BaseModel):
    patient_id: int
    alert_type: str
    severity: AlertSeverity
    description: str
    created_at: datetime

# Clinician models
class Clinician(BaseModel):
    id: int
    email: str
    name: str
    specialization: str
    created_at: datetime

class ClinicianAlert(BaseModel):
    id: int
    clinician_id: int
    patient_id: int
    alert_type: str
    severity: AlertSeverity
    message: str
    created_at: datetime
    status: str = "active"  # active, resolved, dismissed

# API request/response models
class UserCreate(BaseModel):
    """Model for creating a user, used in registration."""
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    date_of_birth: str # Using str for simplicity, can be changed to date
    name: str

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    date_of_birth: str

class ClinicianLogin(BaseModel):
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str

class ConversationRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ConversationResponse(BaseModel):
    session_id: str
    response: str
    agent_type: str
    next_action: Optional[str] = None
    emotional_state: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    analysis: TrendAnalysis

class CompletionResponse(BaseModel):
    completion_message: str
    session_summary: Dict[str, Any]

class PatientSearchRequest(BaseModel):
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    name: Optional[str] = None

class ClinicianAlertRequest(BaseModel):
    patient_id: int
    alert_type: str
    severity: AlertSeverity
    message: str
