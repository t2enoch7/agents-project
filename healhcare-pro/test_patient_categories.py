#!/usr/bin/env python3
"""
Test script for the Patient Reported Outcomes Multi-Agent System
This test demonstrates the full workflow for four different patient categories:
1. Stable/Healthy Patient
2. Patient with Worsening Symptoms
3. Patient with Mental Health Concerns
4. Patient with Chronic Condition Flare-up
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import DatabaseManager
from utils.companion_agent import CompanionAgent
from utils.adaptive_questionnaire_agent import AdaptiveQuestionnaireAgent
from utils.trend_monitoring_agent import TrendMonitoringAgent

class MockDatabaseManager:
    """In-memory mock database for isolated testing."""
    def __init__(self):
        self.patients = {}
        self.sessions = {}
        self.interactions = []
        self.pro_responses = []
        self.alerts = []
        self.next_patient_id = 1
        self.next_session_id = 1
        print("📊 Mock database initialized for new scenario.")

    async def initialize(self):
        pass

    async def create_patient(self, email, date_of_birth, condition="General", **kwargs):
        patient_id = self.next_patient_id
        self.next_patient_id += 1
        self.patients[patient_id] = {"id": patient_id, "email": email, "date_of_birth": date_of_birth, "condition": condition, **kwargs}
        return patient_id

    async def get_patient(self, patient_id):
        return self.patients.get(patient_id)

    async def create_conversation_session(self, patient_id):
        session_id = f"session_{self.next_session_id}"
        self.next_session_id += 1
        self.sessions[session_id] = {"id": session_id, "patient_id": patient_id, "start_time": datetime.now().isoformat()}
        return session_id

    async def store_pro_response(self, patient_id, session_id, question_id, response_value, response_type):
        self.pro_responses.append({"patient_id": patient_id, "session_id": session_id, "question_id": question_id, "response_value": response_value})

    async def get_patient_pro_data(self, patient_id, days=30):
        # Return historical data relevant to the scenario
        patient = self.get_patient(patient_id)
        if patient and "historical_data" in patient:
             return patient["historical_data"] + [r for r in self.pro_responses if r["patient_id"] == patient_id]
        return [r for r in self.pro_responses if r["patient_id"] == patient_id]

    async def store_conversation_interaction(self, **kwargs):
        self.interactions.append(kwargs)

    async def get_session_interactions(self, session_id):
        return [i for i in self.interactions if i["session_id"] == session_id]

    async def create_trend_alert(self, **kwargs):
        print(f"🚨 ALERT CREATED: {kwargs['description']} (Severity: {kwargs['severity']})")
        self.alerts.append(kwargs)

async def run_single_patient_scenario(scenario, agents):
    """Run a full agent workflow for a single patient scenario."""

    db_manager = MockDatabaseManager()
    companion_agent, adaptive_agent, trend_agent = agents
    for agent in agents:
        agent.db_manager = db_manager

    print("\n" + "="*80)
    print(f"🚀 STARTING SCENARIO: {scenario['description']}")
    print("="*80 + "\n")

    # 1. Patient Registration
    patient_id = await db_manager.create_patient(**scenario['patient_data'])
    patient = await db_manager.get_patient(patient_id)
    print(f"👤 Patient '{patient['email']}' registered for condition: '{patient['condition']}'\n")

    # 2. Conversation Start
    session_id = await db_manager.create_conversation_session(patient_id)
    print(f"💬 Session '{session_id}' started.\n")

    history = []

    # 3. Simulate Conversation Flow
    for i, turn in enumerate(scenario['conversation_flow']):
        print(f"--- Turn {i+1} ---")

        if turn['agent'] == 'companion':
            print(f"👤 Patient says: \"{turn['patient_message']}\"")
            analysis = await companion_agent.detect_emotional_state(turn['patient_message'])
            print(f"🧠 Companion emotional analysis: {analysis}")
            response = await companion_agent.generate_follow_up(patient, analysis)
            print(f"🤖 Companion Agent says: \"{response}\"\n")
            history.append({"role": "user", "parts": [turn['patient_message']]})
            history.append({"role": "model", "parts": [response]})

        elif turn['agent'] == 'adaptive':
            print(f"👤 Patient says: \"{turn['patient_message']}\"")
            history.append({"role": "user", "parts": [turn['patient_message']]})

            # Generate and answer questions
            questions_str = await adaptive_agent.process_message(patient, turn['patient_message'], session_id, history)
            print(f"📋 Adaptive Agent asks:\n{questions_str}\n")
            history.append({"role": "model", "parts": [questions_str]})

            # Simulate answering the questions
            answers = turn.get('answers', {})
            if answers:
                print(f"📝 Patient provides answers: {answers}")
                for q_id, resp_val in answers.items():
                    await db_manager.store_pro_response(patient_id, session_id, q_id, resp_val, "multiple_choice")

                # Create a summary of answers for the next turn
                answer_summary = "I've answered the questions. " + " ".join([f"For {q}, I answered {v}." for q, v in answers.items()])
                history.append({"role": "user", "parts": [answer_summary]})

                # Get a concluding message from the adaptive agent
                final_q_response = await adaptive_agent.process_message(patient, answer_summary, session_id, history)
                print(f"🤖 Adaptive Agent says: \"{final_q_response}\"\n")
                history.append({"role": "model", "parts": [final_q_response]})

    # 4. Trend Analysis
    print("--- Final Analysis ---")
    final_analysis = await trend_agent.analyze_and_report(patient_id, session_id)

    print("\n📈 TREND MONITORING AGENT FINAL REPORT:")
    print("-" * 40)
    print(json.dumps(final_analysis, indent=2))
    print("-" * 40)

    print(f"\n✅ SCENARIO '{scenario['description']}' COMPLETE.")


async def main():
    # Define the 4 patient scenarios
    scenarios = [
        {
            "description": "Stable/Healthy Patient",
            "patient_data": {
                "email": "stable.patient@example.com",
                "date_of_birth": "1990-05-20",
                "condition": "General Checkup",
                "historical_data": [
                    {"question_id": "pain_level", "response_value": "2"},
                    {"question_id": "fatigue_level", "response_value": "1"}
                ]
            },
            "conversation_flow": [
                {"agent": "companion", "patient_message": "I'm feeling pretty good this week, nothing much to report."},
                {"agent": "adaptive", "patient_message": "Sure, I can answer some questions.", "answers": {"pain_level": "1", "fatigue_level": "1", "mood": "good"}}
            ]
        },
        {
            "description": "Patient with Worsening Symptoms",
            "patient_data": {
                "email": "worsening.patient@example.com",
                "date_of_birth": "1982-11-10",
                "condition": "Chronic Pain",
                "historical_data": [
                    {"question_id": "pain_level", "response_value": "5"},
                    {"question_id": "sleep_quality", "response_value": "poor"}
                ]
            },
            "conversation_flow": [
                {"agent": "companion", "patient_message": "It's been a rough week. The pain in my back has been getting much worse."},
                {"agent": "adaptive", "patient_message": "Okay, I'll do my best to answer.", "answers": {"pain_level": "8", "medication_effectiveness": "not_effective", "sleep_quality": "very_poor"}}
            ]
        },
        {
            "description": "Patient with Mental Health Concerns",
            "patient_data": {
                "email": "anxious.patient@example.com",
                "date_of_birth": "1995-02-15",
                "condition": "Anxiety",
                "historical_data": [
                    {"question_id": "anxiety_level", "response_value": "moderate"},
                    {"question_id": "mood", "response_value": "okay"}
                ]
            },
            "conversation_flow": [
                {"agent": "companion", "patient_message": "I've been feeling really anxious and on-edge lately. It's hard to relax."},
                {"agent": "adaptive", "patient_message": "I'll answer them.", "answers": {"anxiety_level": "severe", "mood": "irritable", "social_interaction": "avoiding"}}
            ]
        },
        {
            "description": "Patient with Chronic Condition Flare-up (Diabetes)",
            "patient_data": {
                "email": "diabetes.patient@example.com",
                "date_of_birth": "1978-07-30",
                "condition": "Type 2 Diabetes",
                "historical_data": [
                    {"question_id": "blood_sugar_reading", "response_value": "150"},
                    {"question_id": "diet_adherence", "response_value": "mostly"}
                ]
            },
            "conversation_flow": [
                {"agent": "companion", "patient_message": "My blood sugar has been really high, around 250 mg/dL, and I'm feeling very thirsty and tired."},
                {"agent": "adaptive", "patient_message": "Yes, this is concerning. I'll answer the questions.", "answers": {"blood_sugar_reading": "250", "symptoms_dizziness": "yes", "medication_adherence": "yes", "diet_adherence": "poorly"}}
            ]
        }
    ]

    # Initialize agents once
    agents = (CompanionAgent(), AdaptiveQuestionnaireAgent(), TrendMonitoringAgent())

    for scenario in scenarios:
        await run_single_patient_scenario(scenario, agents)

if __name__ == "__main__":
    asyncio.run(main())
