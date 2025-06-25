import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import random

from .models import Patient, AgentResponse, CheckInSchedule
from .database import DatabaseManager

load_dotenv()

logger = logging.getLogger(__name__)

class CompanionAgent:
    def __init__(self):
        """Initialize the Companion Agent with mock responses for testing"""
        self.db_manager = DatabaseManager()

        # Agent personality and capabilities
        self.system_prompt = """
        You are a compassionate healthcare companion agent designed to initiate and maintain engaging conversations with patients managing chronic conditions. Your role is to:

        1. **Build Trust and Rapport**: Create a warm, empathetic connection with patients
        2. **Adapt Communication Style**: Adjust tone, complexity, and delivery based on patient preferences and needs
        3. **Detect Emotional Cues**: Recognize emotional states and respond appropriately
        4. **Support Accessibility**: Ensure communication is accessible for patients with various needs
        5. **Multilingual Support**: Communicate in the patient's preferred language
        6. **Encourage Engagement**: Motivate patients to participate in their care

        Key Guidelines:
        - Always be empathetic and supportive
        - Use simple, clear language unless the patient prefers more complex communication
        - Respect the patient's time and energy levels
        - Be culturally sensitive and inclusive
        - Maintain professional boundaries while being friendly
        - Focus on the patient's well-being and comfort
        """

        # Predefined check-in templates for different conditions
        self.check_in_templates = {
            "diabetes": [
                "How are you feeling today? I'd like to check in on your diabetes management.",
                "Good morning! How did your blood sugar levels look today?",
                "Hi there! How are you managing your diabetes symptoms this week?"
            ],
            "hypertension": [
                "Hello! How are you feeling today? Any changes in your blood pressure?",
                "Good day! How has your blood pressure been this week?",
                "Hi! How are you managing your hypertension symptoms?"
            ],
            "depression": [
                "How are you feeling today? I'm here to listen and support you.",
                "Good morning! How has your mood been this week?",
                "Hi there! How are you coping with your symptoms today?"
            ],
            "chronic_pain": [
                "How are you feeling today? I'd like to check in on your pain levels.",
                "Good morning! How has your pain been this week?",
                "Hi! How are you managing your chronic pain symptoms?"
            ],
            "general": [
                "How are you feeling today? I'd like to check in on your health.",
                "Good morning! How has your week been?",
                "Hi there! How are you managing your condition?"
            ]
        }

    async def get_initial_message(self, patient: Dict[str, Any]) -> str:
        """Generate an initial check-in message for a patient"""
        try:
            # Determine the appropriate template based on patient condition
            condition = patient.get("condition", "").lower()
            template_key = "general"

            for key in self.check_in_templates.keys():
                if key in condition:
                    template_key = key
                    break

            # Select a random template
            template = random.choice(self.check_in_templates[template_key])

            # Personalize the message based on patient preferences
            personalized_message = await self._personalize_message(
                template, patient
            )

            return personalized_message

        except Exception as e:
            logger.error(f"Error generating initial message: {e}")
            return "Hello! How are you feeling today? I'm here to support you."

    async def _personalize_message(self, template: str, patient: Dict[str, Any]) -> str:
        """Personalize a message based on patient characteristics"""
        try:
            # Simple personalization without AI
            condition = patient.get('condition', 'health')
            accessibility = patient.get('accessibility_needs', 'None')

            if accessibility and accessibility != 'None':
                return f"{template} I'll make sure our conversation is accessible for your needs."
            else:
                return f"{template} I'm here to support your {condition} management."

        except Exception as e:
            logger.error(f"Error personalizing message: {e}")
            return template

    async def detect_emotional_state(self, message: str) -> Dict[str, Any]:
        """Detect emotional state from patient message"""
        try:
            # Simple keyword-based emotional analysis
            message_lower = message.lower()

            if any(word in message_lower for word in ['tired', 'exhausted', 'fatigue', 'drained']):
                emotional_state = "fatigued"
                urgency_level = "medium"
            elif any(word in message_lower for word in ['anxious', 'worried', 'stressed', 'nervous']):
                emotional_state = "anxious"
                urgency_level = "medium"
            elif any(word in message_lower for word in ['sad', 'depressed', 'down', 'hopeless']):
                emotional_state = "depressed"
                urgency_level = "high"
            elif any(word in message_lower for word in ['good', 'great', 'better', 'improving']):
                emotional_state = "positive"
                urgency_level = "low"
            else:
                emotional_state = "neutral"
                urgency_level = "low"

            return {
                "emotional_state": emotional_state,
                "confidence_score": 0.7,
                "key_emotions": [emotional_state],
                "urgency_level": urgency_level,
                "suggested_response_tone": "supportive"
            }

        except Exception as e:
            logger.error(f"Error detecting emotional state: {e}")
            return {
                "emotional_state": "neutral",
                "confidence_score": 0.5,
                "key_emotions": [],
                "urgency_level": "low",
                "suggested_response_tone": "supportive"
            }

    async def generate_follow_up(self, patient: Dict[str, Any], emotional_state: Dict[str, Any]) -> str:
        """Generate appropriate follow-up based on emotional state"""
        try:
            emotional = emotional_state.get("emotional_state", "neutral")
            urgency = emotional_state.get("urgency_level", "low")

            if emotional == "depressed" or urgency == "high":
                return "I hear that you're going through a difficult time. It's important to talk to your healthcare provider about these feelings. How can I best support you right now?"
            elif emotional == "anxious":
                return "I understand that you're feeling anxious. Let's take this step by step. What specific concerns do you have about your health?"
            elif emotional == "fatigued":
                return "I can see that you're feeling tired. This is common with chronic conditions. Let's explore what might be contributing to your fatigue."
            else:
                return "Thank you for sharing that with me. Let's continue with some questions to better understand your current health status."

        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            return "I understand. How can I best support you right now?"

    async def schedule_check_in(self, patient_id: int):
        """Schedule a check-in for a patient"""
        try:
            # This would integrate with a scheduling system
            # For now, we'll just log the scheduled check-in
            logger.info(f"Scheduled check-in for patient {patient_id}")

            # In a real implementation, this would:
            # 1. Check patient preferences for timing
            # 2. Schedule the check-in
            # 3. Send notifications
            # 4. Track check-in completion rates

        except Exception as e:
            logger.error(f"Error scheduling check-in: {e}")

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using mock logic instead of Gemini"""
        try:
            # Simple response generation based on keywords
            prompt_lower = prompt.lower()

            if "how are you" in prompt_lower:
                return "I'm here to support you. How are you feeling today?"
            elif "blood sugar" in prompt_lower:
                return "Let's talk about your blood sugar management. What was your most recent reading?"
            elif "medication" in prompt_lower:
                return "Medication adherence is important. Have you taken your prescribed medications today?"
            else:
                return "I'm here to help. What would you like to discuss about your health?"

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm here to support you. How can I help?"

    async def adapt_communication_style(self, patient: Dict[str, Any], message: str) -> str:
        """Adapt communication style based on patient preferences and needs"""
        try:
            accessibility_needs = patient.get('accessibility_needs', '')
            language = patient.get('preferred_language', 'en')

            if accessibility_needs and accessibility_needs != 'None':
                return f"{message} (Adapted for accessibility needs: {accessibility_needs})"
            elif language != 'en':
                return f"{message} (Language preference: {language})"
            else:
                return message

        except Exception as e:
            logger.error(f"Error adapting communication style: {e}")
            return message

    async def generate_completion_message(self, patient: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate a completion message with insights"""
        try:
            condition = patient.get('condition', 'health')
            recommendations = insights.get('recommendations', [])

            message = f"Thank you for sharing your health information with us today. "
            message += f"We've analyzed your {condition} data and have some insights to share. "

            if recommendations:
                message += f"Key recommendations include: {', '.join(recommendations[:2])}. "

            message += "We'll use this information to better support your care. "
            message += "Please continue to monitor your symptoms and reach out if you have any concerns."

            return message

        except Exception as e:
            logger.error(f"Error generating completion message: {e}")
            return "Thank you for sharing your health information. We'll use this to better support your care."
