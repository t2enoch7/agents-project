import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import random

from .models import Patient, AgentResponse, ResponseType
from .database import DatabaseManager

load_dotenv()

logger = logging.getLogger(__name__)

class AdaptiveQuestionnaireAgent:
    def __init__(self):
        """Initialize the Adaptive Questionnaire Agent with mock responses for testing"""
        self.db_manager = DatabaseManager()

        # Agent capabilities and personality
        self.system_prompt = """
        You are an adaptive questionnaire agent designed to collect Patient Reported Outcomes (PROs) through intelligent, personalized conversations. Your role is to:

        1. **Adapt Question Complexity**: Adjust question complexity based on patient comprehension and engagement
        2. **Personalize Question Flow**: Modify question sequence based on patient responses and condition
        3. **Detect Comprehension Issues**: Identify when patients don't understand questions and rephrase them
        4. **Maintain Engagement**: Keep patients engaged through appropriate pacing and tone
        5. **Extract Structured Data**: Convert conversational responses into structured PRO data
        6. **Handle Multiple Response Types**: Support text, numeric, scale, and multiple choice responses

        Key Guidelines:
        - Always be clear and concise
        - Adapt language complexity to patient needs
        - Provide context when needed
        - Use appropriate response formats
        - Maintain conversation flow
        - Respect patient time and energy
        """

        # Question templates for different conditions and response types
        self.question_templates = {
            "diabetes": {
                "blood_sugar": {
                    "text": "What was your blood sugar reading today?",
                    "numeric": "Please enter your blood sugar reading (mg/dL):",
                    "scale": "On a scale of 1-10, how well controlled do you feel your blood sugar has been today? (1=very poor, 10=excellent)"
                },
                "symptoms": {
                    "multiple_choice": "Which diabetes symptoms are you experiencing today? (Select all that apply)",
                    "options": ["Increased thirst", "Frequent urination", "Fatigue", "Blurred vision", "Slow-healing wounds", "None"]
                },
                "medication": {
                    "text": "Did you take your diabetes medication as prescribed today?",
                    "boolean": "Did you take your diabetes medication as prescribed today? (Yes/No)"
                }
            },
            "hypertension": {
                "blood_pressure": {
                    "text": "What was your blood pressure reading today?",
                    "numeric": "Please enter your systolic blood pressure (top number):"
                },
                "symptoms": {
                    "multiple_choice": "Which symptoms are you experiencing? (Select all that apply)",
                    "options": ["Headache", "Shortness of breath", "Chest pain", "Dizziness", "Vision problems", "None"]
                },
                "stress": {
                    "scale": "On a scale of 1-10, how stressed do you feel today? (1=very relaxed, 10=extremely stressed)"
                }
            },
            "depression": {
                "mood": {
                    "scale": "On a scale of 1-10, how would you rate your mood today? (1=very low, 10=excellent)"
                },
                "energy": {
                    "scale": "On a scale of 1-10, how would you rate your energy level today? (1=very low, 10=very high)"
                },
                "sleep": {
                    "text": "How many hours did you sleep last night?",
                    "numeric": "How many hours did you sleep last night?"
                },
                "symptoms": {
                    "multiple_choice": "Which symptoms are you experiencing today? (Select all that apply)",
                    "options": ["Sadness", "Loss of interest", "Fatigue", "Sleep problems", "Appetite changes", "Concentration issues", "None"]
                }
            },
            "chronic_pain": {
                "pain_level": {
                    "scale": "On a scale of 1-10, how would you rate your pain level today? (1=no pain, 10=worst pain imaginable)"
                },
                "pain_location": {
                    "text": "Where is your pain located today?",
                    "multiple_choice": "Where is your pain located today? (Select all that apply)",
                    "options": ["Back", "Neck", "Joints", "Head", "Muscles", "Other"]
                },
                "pain_impact": {
                    "scale": "On a scale of 1-10, how much is pain affecting your daily activities today? (1=not at all, 10=completely)"
                }
            }
        }

        # Patient comprehension and engagement tracking
        self.patient_states = {}

    async def process_message(self, patient: Dict[str, Any], message: str, session_id: str, history: List[Dict[str, Any]]) -> str:
        """Process patient message and generate appropriate response"""
        try:
            # Analyze patient message for comprehension and engagement
            analysis = await self._analyze_patient_response(message, history)

            # Update patient state
            patient_id = patient.get("id")
            if patient_id not in self.patient_states:
                self.patient_states[patient_id] = {
                    "comprehension_level": "medium",
                    "engagement_level": "medium",
                    "response_complexity": "medium",
                    "question_count": 0,
                    "last_response_time": datetime.now()
                }

            # Update state based on analysis
            self._update_patient_state(patient_id, analysis)

            # Generate next question or response
            response = await self._generate_adaptive_response(patient, analysis, history)

            # Store PRO data if applicable
            await self._extract_and_store_pro_data(patient_id, session_id, message, analysis)

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I understand. Could you tell me more about how you're feeling today?"

    async def _analyze_patient_response(self, message: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patient response for comprehension and engagement"""
        try:
            # Simple analysis based on message length and keywords
            message_lower = message.lower()
            message_length = len(message)

            # Determine comprehension level
            if message_length < 10:
                comprehension_level = "low"
            elif message_length > 50:
                comprehension_level = "high"
            else:
                comprehension_level = "medium"

            # Determine engagement level
            if any(word in message_lower for word in ['yes', 'no', 'ok', 'fine']):
                engagement_level = "low"
            elif any(word in message_lower for word in ['because', 'since', 'when', 'how']):
                engagement_level = "high"
            else:
                engagement_level = "medium"

            # Determine response quality
            if message_length > 20 and engagement_level == "high":
                response_quality = "excellent"
            elif message_length > 10:
                response_quality = "good"
            else:
                response_quality = "fair"

            # Extract simple data
            extracted_data = {}
            if "blood sugar" in message_lower or "glucose" in message_lower:
                # Try to extract numbers
                import re
                numbers = re.findall(r'\d+', message)
                if numbers:
                    extracted_data["blood_sugar"] = numbers[0]

            return {
                "comprehension_level": comprehension_level,
                "engagement_level": engagement_level,
                "response_quality": response_quality,
                "emotional_state": "neutral",
                "response_length": "medium" if 10 <= message_length <= 50 else ("short" if message_length < 10 else "long"),
                "comprehension_issues": [],
                "suggested_complexity": "simple" if comprehension_level == "low" else ("complex" if comprehension_level == "high" else "medium"),
                "needs_clarification": False,
                "extracted_data": extracted_data
            }

        except Exception as e:
            logger.error(f"Error analyzing patient response: {e}")
            return {
                "comprehension_level": "medium",
                "engagement_level": "medium",
                "response_quality": "fair",
                "emotional_state": "neutral",
                "response_length": "medium",
                "comprehension_issues": [],
                "suggested_complexity": "medium",
                "needs_clarification": False,
                "extracted_data": {}
            }

    def _update_patient_state(self, patient_id: int, analysis: Dict[str, Any]):
        """Update patient state based on response analysis"""
        try:
            state = self.patient_states[patient_id]

            # Update comprehension level
            if analysis.get("comprehension_level") == "low":
                state["comprehension_level"] = "low"
                state["response_complexity"] = "simple"
            elif analysis.get("comprehension_level") == "high":
                state["comprehension_level"] = "high"
                state["response_complexity"] = "complex"

            # Update engagement level
            state["engagement_level"] = analysis.get("engagement_level", "medium")

            # Update question count
            state["question_count"] += 1

            # Update last response time
            state["last_response_time"] = datetime.now()

        except Exception as e:
            logger.error(f"Error updating patient state: {e}")

    async def _generate_adaptive_response(self, patient: Dict[str, Any], analysis: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
        """Generate adaptive response based on patient state and analysis"""
        try:
            patient_id = patient.get("id")
            state = self.patient_states.get(patient_id, {})
            condition = patient.get("condition", "").lower()

            # Determine next question based on condition and patient state
            next_question = await self._select_next_question(condition, state, analysis, history)

            # Adapt question complexity
            adapted_question = await self._adapt_question_complexity(
                next_question, state.get("response_complexity", "medium"), patient
            )

            # Add clarification if needed
            if analysis.get("needs_clarification"):
                clarification = await self._generate_clarification(analysis)
                return f"{clarification}\n\n{adapted_question}"

            return adapted_question

        except Exception as e:
            logger.error(f"Error generating adaptive response: {e}")
            return "How are you feeling today? Is there anything specific you'd like to share?"

    async def _select_next_question(self, condition: str, state: Dict[str, Any], analysis: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
        """Select the next appropriate question based on condition and patient state"""
        try:
            # Get question templates for the condition
            templates = self.question_templates.get(condition, self.question_templates.get("diabetes"))

            # Determine question category based on history and state
            question_categories = list(templates.keys())

            # Simple logic: cycle through categories
            question_count = state.get("question_count", 0)
            category_index = question_count % len(question_categories)
            category = question_categories[category_index]

            # Get question template for this category
            category_templates = templates[category]

            # Select response type based on patient state
            if state.get("comprehension_level") == "low":
                response_type = "text"  # Simple text response
            elif state.get("engagement_level") == "high":
                response_type = random.choice(["scale", "multiple_choice"])  # More engaging
            else:
                response_type = random.choice(["text", "numeric", "scale"])

            # Get the question template
            if response_type in category_templates:
                question_template = category_templates[response_type]
            else:
                # Fallback to text
                question_template = category_templates.get("text", "How are you feeling today?")

            return question_template

        except Exception as e:
            logger.error(f"Error selecting next question: {e}")
            return "How are you feeling today?"

    async def _adapt_question_complexity(self, question: str, complexity: str, patient: Dict[str, Any]) -> str:
        """Adapt question complexity based on patient needs"""
        try:
            accessibility_needs = patient.get('accessibility_needs', '')
            language = patient.get('preferred_language', 'en')

            if complexity == "simple":
                # Simplify the question
                if "scale of 1-10" in question:
                    return question.replace("scale of 1-10", "scale from 1 to 10")
                elif "mg/dL" in question:
                    return question.replace("mg/dL", "milligrams per deciliter")
                else:
                    return question

            elif complexity == "complex":
                # Add more context
                if "blood sugar" in question.lower():
                    return f"{question} (Normal range is typically 80-120 mg/dL)"
                else:
                    return question

            else:
                return question

        except Exception as e:
            logger.error(f"Error adapting question complexity: {e}")
            return question

    async def _generate_clarification(self, analysis: Dict[str, Any]) -> str:
        """Generate clarification for misunderstood questions"""
        try:
            issues = analysis.get("comprehension_issues", [])

            if "unclear_question" in issues:
                return "Let me rephrase that question more clearly:"
            elif "missing_context" in issues:
                return "Let me provide some context first:"
            elif "complex_language" in issues:
                return "Let me ask this in simpler terms:"
            else:
                return "Let me clarify:"

        except Exception as e:
            logger.error(f"Error generating clarification: {e}")
            return "Let me clarify:"

    async def _extract_and_store_pro_data(self, patient_id: int, session_id: str, message: str, analysis: Dict[str, Any]):
        """Extract PRO data from patient response and store it"""
        try:
            extracted_data = analysis.get("extracted_data", {})

            for key, value in extracted_data.items():
                if value:  # Only store non-empty values
                    await self.db_manager.store_pro_response(
                        patient_id=patient_id,
                        session_id=session_id,
                        question_id=key,
                        response_value=str(value),
                        response_type="text"
                    )

        except Exception as e:
            logger.error(f"Error extracting and storing PRO data: {e}")

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using mock logic instead of Gemini"""
        try:
            # Simple response generation based on keywords
            prompt_lower = prompt.lower()

            if "blood sugar" in prompt_lower:
                return "What was your blood sugar reading today?"
            elif "medication" in prompt_lower:
                return "Have you taken your medication as prescribed today?"
            elif "symptoms" in prompt_lower:
                return "What symptoms are you experiencing today?"
            else:
                return "How are you feeling today?"

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "How are you feeling today?"
