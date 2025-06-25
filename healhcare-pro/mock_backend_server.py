#!/usr/bin/env python3
"""
Simple mock backend server for testing the frontend conversation interface.
This uses Python's built-in HTTP server to avoid SSL issues.
"""

import json
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

class MockConversationAPI:
    """Mock API that simulates the backend conversation endpoints"""

    def __init__(self):
        self.sessions = {}
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

    def start_conversation(self):
        """Start a new conversation session"""
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        # Initialize session
        self.sessions[session_id] = {
            "id": session_id,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "current_step": 0
        }

        # Get first message
        first_step = self.conversation_flow[0]

        return {
            "session_id": session_id,
            "response": first_step["message"],
            "agent_type": first_step["agent_type"],
            "emotional_state": first_step["emotional_state"]
        }

    def continue_conversation(self, message, session_id):
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

    def analyze_trends(self):
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

    def complete_conversation(self, session_id):
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

# Global API instance
api = MockConversationAPI()

class MockBackendHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_request_body(self):
        """Get request body as JSON"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        return {}

    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/health':
            self.send_json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})
        else:
            self.send_json_response({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            if path == '/conversations/start':
                response = api.start_conversation()
                self.send_json_response(response)

            elif path == '/conversations/continue':
                body = self.get_request_body()
                message = body.get('message', '')
                session_id = body.get('session_id', '')

                if not message or not session_id:
                    self.send_json_response({"error": "Missing message or session_id"}, 400)
                    return

                response = api.continue_conversation(message, session_id)
                self.send_json_response(response)

            elif path == '/conversations/analyze':
                response = api.analyze_trends()
                self.send_json_response(response)

            elif path == '/conversations/complete':
                body = self.get_request_body()
                session_id = body.get('session_id', '')

                if not session_id:
                    self.send_json_response({"error": "Missing session_id"}, 400)
                    return

                response = api.complete_conversation(session_id)
                self.send_json_response(response)

            elif path == '/auth/login':
                # Mock login - accept any email/date combination
                body = self.get_request_body()
                email = body.get('email', '')
                date_of_birth = body.get('date_of_birth', '')

                if email and date_of_birth:
                    token = f"mock_token_{uuid.uuid4().hex[:16]}"
                    self.send_json_response({
                        "access_token": token,
                        "token_type": "bearer",
                        "user": {
                            "email": email,
                            "name": email.split('@')[0],
                            "id": "mock_user_123"
                        }
                    })
                else:
                    self.send_json_response({"error": "Invalid credentials"}, 401)

            else:
                self.send_json_response({"error": "Not found"}, 404)

        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

def run_server(port=8001):
    """Run the mock backend server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockBackendHandler)
    print(f"🤖 Mock backend server running on http://localhost:{port}")
    print("📝 Available endpoints:")
    print("  POST /conversations/start - Start a new conversation")
    print("  POST /conversations/continue - Continue conversation")
    print("  POST /conversations/analyze - Analyze trends")
    print("  POST /conversations/complete - Complete conversation")
    print("  POST /auth/login - Mock login")
    print("  GET /health - Health check")
    print("\nPress Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
