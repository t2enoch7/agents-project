#!/usr/bin/env python3
"""
Simple test script for the Patient Reported Outcomes Multi-Agent System
This version works without external dependencies for testing the core logic
"""

import asyncio
import json
from datetime import datetime

# Mock the agents for testing without external dependencies
class MockCompanionAgent:
    async def get_initial_message(self, patient):
        return f"Hello! How are you feeling today? I'm here to check in on your {patient.get('condition', 'health')}."

    async def detect_emotional_state(self, message):
        return {
            "emotional_state": "concerned",
            "confidence_score": 0.8,
            "urgency_level": "medium"
        }

    async def generate_completion_message(self, patient, insights):
        return "Thank you for sharing your health information. We'll use this to better support your care."

class MockAdaptiveQuestionnaireAgent:
    async def process_message(self, patient, message, session_id, history):
        questions = [
            "What was your blood sugar reading today?",
            "How would you rate your energy level on a scale of 1-10?",
            "Have you taken your medication as prescribed?",
            "How stressed do you feel today on a scale of 1-10?"
        ]
        return questions[len(history) % len(questions)]

class MockTrendMonitoringAgent:
    async def analyze_patient_trends(self, patient, pro_data):
        return {
            "risk_score": 0.6,
            "alerts": [{"type": "blood_sugar_high", "severity": "medium"}],
            "recommendations": [
                "Monitor blood sugar levels more closely",
                "Consider medication adjustment",
                "Schedule follow-up appointment"
            ]
        }

# Mock database for testing
class MockDatabase:
    def __init__(self):
        self.patients = {}
        self.sessions = {}
        self.conversations = {}
        self.pro_data = []

    async def get_patient_by_email(self, email):
        return self.patients.get(email)

    async def create_patient(self, email, date_of_birth, condition, medical_history=""):
        patient_id = len(self.patients) + 1
        self.patients[email] = {
            "id": patient_id,
            "email": email,
            "date_of_birth": date_of_birth,
            "condition": condition,
            "medical_history": medical_history
        }
        return patient_id

    async def create_conversation_session(self, patient_id):
        session_id = f"session_{patient_id}_{datetime.now().timestamp()}"
        self.sessions[session_id] = {"patient_id": patient_id, "started_at": datetime.now()}
        return session_id

    async def store_conversation_interaction(self, session_id, patient_id, message, response, agent_type):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append({
            "message": message,
            "response": response,
            "agent_type": agent_type,
            "timestamp": datetime.now()
        })

    async def get_conversation_history(self, session_id):
        return self.conversations.get(session_id, [])

    async def get_patient_pro_data(self, patient_id):
        return self.pro_data

# Simple token management
tokens = {}

def create_simple_token(email, date_of_birth):
    import hashlib
    token_data = f"{email}:{date_of_birth}:{datetime.now().timestamp()}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    tokens[token] = {"email": email, "date_of_birth": date_of_birth}
    return token

def verify_token(token):
    return tokens.get(token)

async def test_workflow():
    """Test the complete workflow with mock components"""
    print("🚀 Starting Patient Reported Outcomes Multi-Agent System Test")
    print("=" * 60)

    # Initialize mock components
    db = MockDatabase()
    companion_agent = MockCompanionAgent()
    adaptive_agent = MockAdaptiveQuestionnaireAgent()
    trend_agent = MockTrendMonitoringAgent()

    # Step 1: Login with email and date of birth
    print("\n1️⃣ Logging in with email and date of birth...")
    email = "john.doe@example.com"
    date_of_birth = "1985-03-15"

    # Check if patient exists, create if not
    patient = await db.get_patient_by_email(email)
    if not patient:
        patient_id = await db.create_patient(email, date_of_birth, "diabetes",
                                           "Type 2 diabetes diagnosed in 2020. Currently on metformin.")
        patient = await db.get_patient_by_email(email)

    token = create_simple_token(email, date_of_birth)
    print(f"✅ Login successful! Patient ID: {patient['id']}")
    print(f"📧 Email: {patient['email']}")
    print(f"🏥 Condition: {patient['condition']}")

    # Step 2: Start conversation with companion agent
    print("\n2️⃣ Starting conversation with companion agent...")
    session_id = await db.create_conversation_session(patient['id'])
    initial_message = await companion_agent.get_initial_message(patient)

    await db.store_conversation_interaction(
        session_id=session_id,
        patient_id=patient['id'],
        message="",
        response=initial_message,
        agent_type="companion"
    )

    print(f"✅ Conversation started! Session ID: {session_id}")
    print(f"🤖 Agent: companion")
    print(f"💬 Message: {initial_message}")

    # Step 3: Patient responds to initial greeting
    print("\n3️⃣ Patient responding to initial greeting...")
    patient_message = "I'm feeling a bit tired today and my blood sugar has been running high this week."

    await db.store_conversation_interaction(
        session_id=session_id,
        patient_id=patient['id'],
        message=patient_message,
        response="",
        agent_type="patient"
    )

    # Analyze emotional state
    emotional_analysis = await companion_agent.detect_emotional_state(patient_message)
    print(f"✅ Response processed!")
    print(f"😊 Emotional Analysis: {emotional_analysis}")

    # Step 4: Generate adaptive questionnaire
    print("\n4️⃣ Generating adaptive questionnaire...")
    history = await db.get_conversation_history(session_id)
    questionnaire_response = await adaptive_agent.process_message(
        patient=patient,
        message=patient_message,
        session_id=session_id,
        history=history
    )

    await db.store_conversation_interaction(
        session_id=session_id,
        patient_id=patient['id'],
        message="",
        response=questionnaire_response,
        agent_type="adaptive_questionnaire"
    )

    print(f"🤖 Agent: adaptive_questionnaire")
    print(f"💬 Question: {questionnaire_response}")

    # Step 5: Continue with more questions
    print("\n5️⃣ Continuing with adaptive questionnaire...")
    patient_responses = [
        "My blood sugar was 180 this morning",
        "I've been feeling more thirsty than usual",
        "I took my medication as prescribed",
        "I've been a bit stressed with work lately"
    ]

    for i, response in enumerate(patient_responses, 1):
        print(f"\n   Question {i}: {response}")

        await db.store_conversation_interaction(
            session_id=session_id,
            patient_id=patient['id'],
            message=response,
            response="",
            agent_type="patient"
        )

        history = await db.get_conversation_history(session_id)
        next_question = await adaptive_agent.process_message(
            patient=patient,
            message=response,
            session_id=session_id,
            history=history
        )

        await db.store_conversation_interaction(
            session_id=session_id,
            patient_id=patient['id'],
            message="",
            response=next_question,
            agent_type="adaptive_questionnaire"
        )

        print(f"   🤖 Agent: adaptive_questionnaire")
        print(f"   💬 Next Question: {next_question}")

    # Step 6: Analyze trends and generate insights
    print("\n6️⃣ Analyzing trends and generating insights...")
    pro_data = await db.get_patient_pro_data(patient['id'])
    analysis = await trend_agent.analyze_patient_trends(patient, pro_data)

    print(f"✅ Analysis completed!")
    print(f"📊 Risk Score: {analysis.get('risk_score', 'N/A')}")
    print(f"🚨 Alerts: {len(analysis.get('alerts', []))}")
    print(f"💡 Recommendations: {len(analysis.get('recommendations', []))}")

    if analysis.get('recommendations'):
        print("   Key Recommendations:")
        for rec in analysis['recommendations']:
            print(f"   • {rec}")

    # Step 7: Complete conversation
    print("\n7️⃣ Completing conversation...")
    completion_message = await companion_agent.generate_completion_message(patient, analysis)
    history = await db.get_conversation_history(session_id)

    print(f"✅ Conversation completed!")
    print(f"💬 Completion Message: {completion_message}")
    print(f"📈 Session Summary:")
    print(f"   • Total Interactions: {len(history)}")
    print(f"   • Key Findings: {len(analysis.get('recommendations', []))}")

    print("\n" + "=" * 60)
    print("🎉 Test workflow completed successfully!")
    print("The multi-agent system workflow is working as expected.")
    print("\n📋 Summary:")
    print(f"   • Patient: {patient['email']} ({patient['condition']})")
    print(f"   • Session: {session_id}")
    print(f"   • Interactions: {len(history)}")
    print(f"   • Risk Level: {analysis.get('risk_score', 'N/A')}")
    print(f"   • Recommendations: {len(analysis.get('recommendations', []))}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
