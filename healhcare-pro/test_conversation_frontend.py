#!/usr/bin/env python3
"""
Test script to demonstrate the conversation flow that the frontend will use.
This simulates the backend API responses without requiring FastAPI.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List

class MockConversationAPI:
    """Mock API that simulates the backend conversation endpoints"""

    def __init__(self):
        self.sessions = {}
        self.session_counter = 0
        self.conversation_flow = [
            {
                "agent_type": "companion",
                "message": "Hello! I'm your AI health companion. I'm here to help you with a personalized health check-in today. How are you feeling right now?",
                "emotional_state": None
            },
            {
                "agent_type": "adaptive_questionnaire",
                "message": "Thank you for sharing that. I'd like to ask you a few questions to better understand your current health status. On a scale of 1-10, how would you rate your energy level today?",
                "emotional_state": {"mood": "neutral", "confidence": 0.7}
            },
            {
                "agent_type": "adaptive_questionnaire",
                "message": "I see. How about your sleep quality last night? Did you get enough rest?",
                "emotional_state": {"mood": "concerned", "confidence": 0.8}
            },
            {
                "agent_type": "adaptive_questionnaire",
                "message": "That's helpful to know. Have you been experiencing any pain or discomfort recently? If so, can you describe where and how it feels?",
                "emotional_state": {"mood": "attentive", "confidence": 0.9}
            },
            {
                "agent_type": "trend_monitoring",
                "message": "I'm analyzing your responses and comparing them to your previous check-ins. I notice some patterns that might be worth discussing with your healthcare provider.",
                "emotional_state": {"mood": "analytical", "confidence": 0.95}
            }
        ]
        self.current_step = 0

    def start_conversation(self) -> Dict[str, Any]:
        """Start a new conversation session"""
        self.session_counter += 1
        session_id = f"session_{self.session_counter}_{int(time.time())}"

        # Initialize session
        self.sessions[session_id] = {
            "id": session_id,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "current_step": 0,
            "patient_id": "test_patient_123"
        }

        # Get first message
        first_step = self.conversation_flow[0]

        return {
            "session_id": session_id,
            "response": first_step["message"],
            "agent_type": first_step["agent_type"],
            "emotional_state": first_step["emotional_state"]
        }

    def continue_conversation(self, message: str, session_id: str) -> Dict[str, Any]:
        """Continue the conversation with a user message"""
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        session = self.sessions[session_id]
        session["messages"].append({
            "text": message,
            "sender": "user",
            "timestamp": datetime.now().isoformat()
        })

        # Move to next step
        session["current_step"] += 1

        if session["current_step"] < len(self.conversation_flow):
            step = self.conversation_flow[session["current_step"]]

            # Add agent response to session
            session["messages"].append({
                "text": step["message"],
                "sender": "agent",
                "agent_type": step["agent_type"],
                "timestamp": datetime.now().isoformat()
            })

            return {
                "response": step["message"],
                "agent_type": step["agent_type"],
                "emotional_state": step["emotional_state"]
            }
        else:
            # Conversation complete
            return {
                "response": "Thank you for completing your health check-in. I'll analyze your responses and provide you with a summary.",
                "agent_type": "companion",
                "emotional_state": {"mood": "satisfied", "confidence": 1.0}
            }

    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze conversation trends and generate insights"""
        return {
            "analysis": {
                "data_points": 5,
                "risk_score": 0.3,
                "trends": [
                    "Consistent energy level reporting",
                    "Sleep quality variations detected",
                    "No immediate health concerns identified"
                ],
                "recommendations": [
                    "Consider maintaining regular sleep schedule",
                    "Continue monitoring energy levels",
                    "Schedule follow-up with healthcare provider in 2 weeks"
                ],
                "alerts": []
            }
        }

    def complete_conversation(self, session_id: str) -> Dict[str, Any]:
        """Complete the conversation session"""
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        session = self.sessions[session_id]
        session["completed_at"] = datetime.now().isoformat()

        return {
            "completion_message": "Thank you for your time today! Your health check-in has been completed and analyzed. I've identified some positive patterns in your responses. Remember to stay hydrated and maintain your regular exercise routine. If you have any concerns, don't hesitate to reach out to your healthcare provider. Take care!",
            "session_summary": {
                "total_messages": len(session["messages"]),
                "duration_minutes": 5,
                "key_insights": [
                    "Patient shows good self-awareness",
                    "No immediate health risks detected",
                    "Recommendation: Continue current health practices"
                ]
            }
        }

def test_conversation_flow():
    """Test the complete conversation flow"""
    print("🤖 Testing AI Conversation Flow")
    print("=" * 50)

    api = MockConversationAPI()

    # Start conversation
    print("\n1. Starting conversation...")
    start_response = api.start_conversation()
    print(f"Session ID: {start_response['session_id']}")
    print(f"Agent: {start_response['response']}")
    print(f"Agent Type: {start_response['agent_type']}")

    session_id = start_response['session_id']

    # Simulate user responses
    user_responses = [
        "I'm feeling pretty good today, maybe a 7 out of 10.",
        "I slept okay, about 7 hours but woke up a few times.",
        "No significant pain, just some minor stiffness in my lower back from sitting at work."
    ]

    for i, response in enumerate(user_responses, 1):
        print(f"\n{i+1}. User: {response}")
        continue_response = api.continue_conversation(response, session_id)
        print(f"Agent: {continue_response['response']}")
        print(f"Agent Type: {continue_response['agent_type']}")
        if continue_response['emotional_state']:
            print(f"Emotional State: {continue_response['emotional_state']}")

    # Analyze trends
    print(f"\n{len(user_responses)+2}. Analyzing trends...")
    analysis = api.analyze_trends()
    print("Analysis Results:")
    print(f"  - Data Points: {analysis['analysis']['data_points']}")
    print(f"  - Risk Score: {analysis['analysis']['risk_score']}")
    print(f"  - Trends: {', '.join(analysis['analysis']['trends'])}")
    print(f"  - Recommendations: {', '.join(analysis['analysis']['recommendations'])}")

    # Complete conversation
    print(f"\n{len(user_responses)+3}. Completing conversation...")
    completion = api.complete_conversation(session_id)
    print(f"Completion Message: {completion['completion_message']}")
    print(f"Session Summary: {completion['session_summary']}")

    print("\n✅ Conversation flow test completed successfully!")
    print("\nThis demonstrates how the frontend will interact with the backend AI agents:")
    print("- Companion Agent initiates check-ins")
    print("- Adaptive Questionnaire Agent personalizes questions")
    print("- Trend Monitoring Agent analyzes patterns")
    print("- All agents work together to provide comprehensive health insights")

if __name__ == "__main__":
    test_conversation_flow()
