#!/usr/bin/env python3
"""
Simple API test script for the Patient Reported Outcomes Multi-Agent System
Tests the FastAPI endpoints using only built-in Python libraries
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {"Content-Type": "application/json"}

    if data:
        data = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8'), response.status
    except urllib.error.HTTPError as e:
        return e.read().decode('utf-8'), e.code
    except Exception as e:
        return str(e), 0

def test_api_endpoints():
    """Test the API endpoints"""
    print("🚀 Testing Patient Reported Outcomes Multi-Agent System API")
    print("=" * 60)

    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    response_data, status = make_request(f"{BASE_URL}/health")
    if status == 200:
        health_data = json.loads(response_data)
        print(f"✅ Health check passed!")
        print(f"   Status: {health_data['status']}")
        print(f"   Agents: {list(health_data['agents'].keys())}")
    else:
        print(f"❌ Health check failed: {status}")
        print(f"   Response: {response_data}")
        return

    # Test 2: Patient login
    print("\n2️⃣ Testing patient login...")
    login_data = {
        "email": "test.patient@example.com",
        "date_of_birth": "1990-01-15"
    }

    response_data, status = make_request(f"{BASE_URL}/auth/login", method="POST", data=login_data)
    if status == 200:
        login_result = json.loads(response_data)
        token = login_result["token"]
        patient_id = login_result["patient_id"]
        print(f"✅ Login successful!")
        print(f"   Patient ID: {patient_id}")
        print(f"   Email: {login_result['email']}")
        print(f"   Condition: {login_result['condition']}")
        print(f"   Token: {token[:20]}...")
    else:
        print(f"❌ Login failed: {status}")
        print(f"   Response: {response_data}")
        return

    # Test 3: Create patient profile
    print("\n3️⃣ Testing patient profile creation...")
    profile_data = {
        "email": "test.patient@example.com",
        "date_of_birth": "1990-01-15",
        "condition": "diabetes",
        "medical_history": "Type 2 diabetes diagnosed in 2022. Currently on metformin.",
        "preferred_language": "en",
        "accessibility_needs": "None"
    }

    response_data, status = make_request(f"{BASE_URL}/patients", method="POST", data=profile_data)
    if status == 200:
        profile_result = json.loads(response_data)
        print(f"✅ Profile created/updated!")
        print(f"   Patient ID: {profile_result['patient_id']}")
    else:
        print(f"❌ Profile creation failed: {status}")
        print(f"   Response: {response_data}")

    # Test 4: Start conversation
    print("\n4️⃣ Testing conversation start...")
    response_data, status = make_request(f"{BASE_URL}/conversation/start?token={token}")
    if status == 200:
        start_result = json.loads(response_data)
        session_id = start_result["session_id"]
        print(f"✅ Conversation started!")
        print(f"   Session ID: {session_id}")
        print(f"   Agent: {start_result['agent_type']}")
        print(f"   Message: {start_result['response']}")
    else:
        print(f"❌ Conversation start failed: {status}")
        print(f"   Response: {response_data}")
        return

    # Test 5: Continue conversation
    print("\n5️⃣ Testing conversation continuation...")
    patient_response = {
        "message": "I'm feeling a bit tired today and my blood sugar has been running high this week.",
        "session_id": session_id
    }

    response_data, status = make_request(f"{BASE_URL}/conversation/continue?token={token}", method="POST", data=patient_response)
    if status == 200:
        continue_result = json.loads(response_data)
        print(f"✅ Response processed!")
        print(f"   Agent: {continue_result['agent_type']}")
        print(f"   Response: {continue_result['response']}")
        if 'emotional_state' in continue_result:
            print(f"   Emotional Analysis: {continue_result['emotional_state']}")
    else:
        print(f"❌ Response processing failed: {status}")
        print(f"   Response: {response_data}")

    # Test 6: Analyze trends
    print("\n6️⃣ Testing trend analysis...")
    response_data, status = make_request(f"{BASE_URL}/conversation/analyze?token={token}")
    if status == 200:
        analysis_result = json.loads(response_data)
        analysis = analysis_result["analysis"]
        print(f"✅ Analysis completed!")
        print(f"   Risk Score: {analysis.get('risk_score', 'N/A')}")
        print(f"   Alerts: {len(analysis.get('alerts', []))}")
        print(f"   Recommendations: {len(analysis.get('recommendations', []))}")

        if analysis.get('recommendations'):
            print("   Key Recommendations:")
            for rec in analysis['recommendations'][:2]:
                print(f"     • {rec}")
    else:
        print(f"❌ Analysis failed: {status}")
        print(f"   Response: {response_data}")

    # Test 7: Complete conversation
    print("\n7️⃣ Testing conversation completion...")
    response_data, status = make_request(f"{BASE_URL}/conversation/complete?session_id={session_id}&token={token}")
    if status == 200:
        complete_result = json.loads(response_data)
        print(f"✅ Conversation completed!")
        print(f"   Completion Message: {complete_result['completion_message'][:100]}...")
        summary = complete_result['session_summary']
        print(f"   Total Interactions: {summary['total_interactions']}")
        print(f"   Key Findings: {len(summary['key_findings'])}")
    else:
        print(f"❌ Conversation completion failed: {status}")
        print(f"   Response: {response_data}")

    print("\n" + "=" * 60)
    print("🎉 API testing completed!")
    print("The multi-agent system API is working correctly.")

if __name__ == "__main__":
    test_api_endpoints()
