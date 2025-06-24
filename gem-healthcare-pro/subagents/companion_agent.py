import logging
import uuid
from google.generative_agent import AgentState
from google.adk.agents import LlmAgent # New import for LlmAgent
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CompanionPhaseAgent: # Renamed to better reflect its role as a phase handler
    """
    The CompanionPhaseAgent handles the initial conversational check-in.
    It takes an AgentState, updates it with the greeting, and prepares for the
    Adaptive Questionnaire phase. It relies on internal LlmAgent for generation.
    """
    def __init__(self, model_config: dict = None):
        self.model_config = model_config if model_config is not None else {'temperature': 0.5}

        self.greeting_llm = LlmAgent(
            name="CompanionGreetingLLM",
            instruction=(
                "You are a friendly healthcare companion AI. Start a gentle, empathetic "
                "check-in with a patient managing a chronic condition. "
                "Ask them how they are feeling today and if they'd like to share anything about their health. "
                "Ensure the tone is warm and supportive. Keep it brief and inviting. "
                "Output the generated greeting to 'companion_greeting'."
            ),
            output_key="companion_greeting", # Store the greeting in the state
            model_name='gemini-1.5-flash',
            generation_config=self.model_config
        )
        logging.info("CompanionPhaseAgent initialized.")

    def invoke(self, state: AgentState):
        """
        Invokes the Companion Agent's logic, updating the shared AgentState.
        Args:
            state: The current AgentState for the patient's PRO journey.
                   Expected to contain 'patient_id'.
                   Will update 'session_id', 'conversation_history', 'current_agent_phase'.
        """
        patient_id = state.get('patient_id')
        if not patient_id:
            logging.error("CompanionPhaseAgent requires 'patient_id' in AgentState.")
            state.set('error_message', "Initialization error: Patient ID missing.")
            return

        # Initialize session ID if not already present (first run for a patient)
        if not state.get('session_id'):
            state.set('session_id', str(uuid.uuid4()))
            logging.info(f"Generated new session ID: {state.get('session_id')}")

        # Invoke the LLM to get the initial greeting
        logging.info(f"CompanionPhaseAgent invoking greeting LLM for patient {patient_id}.")
        self.greeting_llm.invoke(state) # This will write to state['companion_greeting']

        greeting_text = state.get('companion_greeting', "Hello! How are you feeling today?")

        # Initialize conversation history if it's empty
        if not state.get('conversation_history'):
            state.set('conversation_history', [])

        # Add the greeting to the conversation history
        history = state.get('conversation_history')
        history.append({'role': 'assistant', 'text': greeting_text})
        state.set('conversation_history', history)

        # Update the current phase to indicate handoff to adaptive questionnaire
        state.set('current_agent_phase', 'adaptive_questionnaire_agent')
        state.set('agent_response', greeting_text) # Set the response to be shown to the user
        state.set('status', 'awaiting_patient_response') # Indicate system is waiting for user input

        logging.info(f"CompanionPhaseAgent completed for patient {patient_id}. Next phase: {state.get('current_agent_phase')}")

