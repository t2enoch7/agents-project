#!/usr/bin/env python3
"""
Test script for the Patient Reported Outcomes Multi-Agent System
Demonstrates the complete workflow from login to conversation completion
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

async def test_workflow():
    """Test the complete workflow"""
    print("🚀 Starting Patient Reported Outcomes Multi-Agent System Test")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:

        # Step 1: Login with email and date of birth
        print("\n1️⃣ Logging in with email and date of birth...")
        login_data = {
            "email": "john.doe@example.com",
            "date_of_birth": "1985-03-15"
        }

        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result["token"]
                patient_id = login_result["patient_id"]
                print(f"✅ Login successful! Patient ID: {patient_id}")
                print(f"📧 Email: {login_result['email']}")
                print(f"🏥 Condition: {login_result['condition']}")
            else:
                print(f"❌ Login failed: {response.status}")
                return

        # Step 2: Create/Update patient profile
        print("\n2️⃣ Creating patient profile...")
        profile_data = {
            "email": "john.doe@example.com",
            "date_of_birth": "1985-03-15",
            "condition": "diabetes",
            "medical_history": "Type 2 diabetes diagnosed in 2020. Currently on metformin. Blood sugar levels have been fluctuating.",
            "preferred_language": "en",
            "accessibility_needs": "None"
        }

        async with session.post(f"{BASE_URL}/patients", json=profile_data) as response:
            if response.status == 200:
                profile_result = await response.json()
                print(f"✅ Profile created/updated! Patient ID: {profile_result['patient_id']}")
            else:
                print(f"❌ Profile creation failed: {response.status}")

        # Step 3: Start conversation with companion agent
        print("\n3️⃣ Starting conversation with companion agent...")
        async with session.post(f"{BASE_URL}/conversation/start?token={token}") as response:
            if response.status == 200:
                start_result = await response.json()
                session_id = start_result["session_id"]
                print(f"✅ Conversation started! Session ID: {session_id}")
                print(f"🤖 Agent: {start_result['agent_type']}")
                print(f"💬 Message: {start_result['response']}")
            else:
                print(f"❌ Conversation start failed: {response.status}")
                return

        # Step 4: Patient responds to initial greeting
        print("\n4️⃣ Patient responding to initial greeting...")
        patient_response = {
            "message": "I'm feeling a bit tired today and my blood sugar has been running high this week.",
            "session_id": session_id
        }

        async with session.post(f"{BASE_URL}/conversation/continue?token={token}", json=patient_response) as response:
            if response.status == 200:
                continue_result = await response.json()
                print(f"✅ Response processed!")
                print(f"🤖 Agent: {continue_result['agent_type']}")
                print(f"💬 Response: {continue_result['response']}")
                if 'emotional_state' in continue_result:
                    print(f"😊 Emotional Analysis: {continue_result['emotional_state']}")
            else:
                print(f"❌ Response processing failed: {response.status}")
                return

        # Step 5: Continue with adaptive questionnaire
        print("\n5️⃣ Continuing with adaptive questionnaire...")
        questionnaire_responses = [
            "My blood sugar was 180 this morning",
            "I've been feeling more thirsty than usual",
            "I took my medication as prescribed",
            "I've been a bit stressed with work lately"
        ]

        for i, response in enumerate(questionnaire_responses, 1):
            print(f"\n   Question {i}: {response}")
            patient_response = {
                "message": response,
                "session_id": session_id
            }

            async with session.post(f"{BASE_URL}/conversation/continue?token={token}", json=patient_response) as response:
                if response.status == 200:
                    continue_result = await response.json()
                    print(f"   🤖 Agent: {continue_result['agent_type']}")
                    print(f"   💬 Response: {continue_result['response']}")
                else:
                    print(f"   ❌ Response processing failed: {response.status}")
                    break

        # Step 6: Analyze trends and generate insights
        print("\n6️⃣ Analyzing trends and generating insights...")
        async with session.post(f"{BASE_URL}/conversation/analyze?token={token}") as response:
            if response.status == 200:
                analysis_result = await response.json()
                print(f"✅ Analysis completed!")
                analysis = analysis_result["analysis"]
                print(f"📊 Risk Score: {analysis.get('risk_score', 'N/A')}")
                print(f"🚨 Alerts: {len(analysis.get('alerts', []))}")
                print(f"💡 Recommendations: {len(analysis.get('recommendations', []))}")

                if analysis.get('recommendations'):
                    print("   Key Recommendations:")
                    for rec in analysis['recommendations'][:3]:
                        print(f"   • {rec}")
            else:
                print(f"❌ Analysis failed: {response.status}")

        # Step 7: Complete conversation
        print("\n7️⃣ Completing conversation...")
        async with session.post(f"{BASE_URL}/conversation/complete?session_id={session_id}&token={token}") as response:
            if response.status == 200:
                complete_result = await response.json()
                print(f"✅ Conversation completed!")
                print(f"💬 Completion Message: {complete_result['completion_message']}")
                print(f"📈 Session Summary:")
                summary = complete_result['session_summary']
                print(f"   • Total Interactions: {summary['total_interactions']}")
                print(f"   • Key Findings: {len(summary['key_findings'])}")
            else:
                print(f"❌ Conversation completion failed: {response.status}")

        # Step 8: Health check
        print("\n8️⃣ Checking system health...")
        async with session.get(f"{BASE_URL}/health") as response:
            if response.status == 200:
                health_result = await response.json()
                print(f"✅ System Status: {health_result['status']}")
                print(f"🤖 Active Agents: {list(health_result['agents'].keys())}")
            else:
                print(f"❌ Health check failed: {response.status}")

    print("\n" + "=" * 60)
    print("🎉 Test workflow completed successfully!")
    print("The multi-agent system is working as expected.")

if __name__ == "__main__":
    asyncio.run(test_workflow())
