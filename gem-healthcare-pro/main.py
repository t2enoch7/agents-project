# main.py

import os
import logging
import json # Added for pretty printing JSON output in response

from google.generative_agent import AgentState
from google.adk.agents import SequentialAgent
from google.adk import agent_util

from subagents.companion_agent import CompanionPhaseAgent
from subagents.adaptive_questionnaire_agent import AdaptiveQuestionnairePhaseAgent
from subagents.trend_monitoring_agent import TrendMonitoringPhaseAgent
from utils.firestore_utils import initialize_firestore_client, save_state, load_state, log_event

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PROWorkflowAgent(SequentialAgent):
    """
    The top-level SequentialAgent orchestrating the Patient Reported Outcomes workflow.
    It manages the overall state and transitions between different phases (Companion,
    Adaptive Questionnaire, Trend Monitoring).
    """
    def __init__(self, patient_id: str):
        super().__init__(name="PROWorkflowAgent", sub_agents=[]) # Sub-agents will be added dynamically

        self.patient_id = patient_id

        # Instantiate the phase handlers
        self.companion_phase = CompanionPhaseAgent()
        self.adaptive_phase = AdaptiveQuestionnairePhaseAgent()
        self.trend_monitoring_phase = TrendMonitoringPhaseAgent()

        # Initial state for a new patient or loaded from Firestore
        self.state = AgentState(
            initial_state={
                'patient_id': patient_id,
                'current_agent_phase': 'initial', # 'initial', 'companion_agent', 'adaptive_questionnaire_agent', 'trend_monitoring_agent', 'completed'
                'conversation_history': [],
                'pro_data_collected': {},
                'current_question_index': 0,
                'questions_asked_count': 0,
                'max_questions_per_session': 5, # Configurable
                'session_id': None, # Set by CompanionAgent
                'last_analysis_timestamp': None,
                'alerts_triggered_history': [],
                'agent_response': "Welcome! Let's start your health check-in.", # Initial message
                'status': 'ready_to_start' # 'ready_to_start', 'awaiting_patient_response', 'ask_question', 'session_complete', 'analysis_complete', 'error'
            }
        )
        # Load persistent state if available
        self._load_workflow_state()
        logging.info(f"PROWorkflowAgent initialized for patient {self.patient_id}. Current phase: {self.state.get('current_agent_phase')}")

    def _load_workflow_state(self):
        """Loads the entire workflow state from Firestore."""
        loaded_data = load_state('pro_workflow_states', self.patient_id)
        if loaded_data:
            self.state.update_state(loaded_data)
            logging.info(f"PROWorkflowAgent state loaded for patient {self.patient_id}.")
        else:
            logging.info(f"No existing workflow state found for patient {self.patient_id}. Using initial state.")

    def _save_workflow_state(self):
        """Saves the entire workflow state to Firestore."""
        save_state('pro_workflow_states', self.patient_id, self.state.as_dict())
        logging.info(f"PROWorkflowAgent state saved for patient {self.patient_id}.")

    def invoke(self, input_state: AgentState):
        """
        The main invocation method for the PROWorkflowAgent.
        It orchestrates the flow based on the current phase.
        Args:
            input_state: The input AgentState, typically containing the 'patient_response'
                         from the user for the current turn.
        """
        # Update the main state with the latest user input
        if input_state.get('patient_response'):
            self.state.set('patient_response', input_state.get('patient_response'))
            # Reset initial_trigger after first use
            self.state.set('initial_trigger', False)
        elif input_state.get('initial_trigger'): # This means it's the very first invocation
            self.state.set('initial_trigger', True)

        log_event("PROWorkflow_invoke", self.patient_id, {
            "current_phase": self.state.get('current_agent_phase'),
            "patient_response": self.state.get('patient_response')
        })

        current_phase = self.state.get('current_agent_phase')

        # Dispatch to the appropriate phase agent
        if current_phase == 'initial' or current_phase == 'companion_agent':
            logging.info(f"Dispatching to CompanionPhaseAgent for patient {self.patient_id}.")
            self.companion_phase.invoke(self.state)

        # Check current_agent_phase again, as it might have changed after the previous invoke
        if self.state.get('current_agent_phase') == 'adaptive_questionnaire_agent':
            logging.info(f"Dispatching to AdaptiveQuestionnairePhaseAgent for patient {self.patient_id}.")
            self.adaptive_phase.invoke(self.state)

        # Check current_agent_phase again, as it might have changed after the previous invoke
        if self.state.get('current_agent_phase') == 'trend_monitoring_agent':
            logging.info(f"Dispatching to TrendMonitoringPhaseAgent for patient {self.patient_id}.")
            self.trend_monitoring_phase.invoke(self.state)

        # After any phase, save the updated state
        self._save_workflow_state()

        # The invoke method of a SequentialAgent implicitly returns the modified state.
        # However, for the ADK `agent_callback` signature, we need to return a string.
        # We extract the relevant user-facing response from the internal state.

        # For the ADK web interface, we want to return a summary of the current turn.
        # This part requires careful formatting for user readability.
        response_parts = []
        if self.state.get('patient_response'):
            response_parts.append(f"Patient Response: {self.state.get('patient_response')}")

        system_response = self.state.get('agent_response', '...')
        response_parts.append(f"System: {system_response}")

        if self.state.get('status') == 'analysis_complete':
            response_parts.append(f"\n--- Trend Analysis ---")
            response_parts.append(f"Summary: {self.state.get('analysis_summary', 'N/A')}")
            risk_signals = self.state.get('risk_signals_detected', [])
            response_parts.append(f"Risk Signals: {', '.join(risk_signals) if risk_signals else 'None'}")
            generated_alert = self.state.get('generated_alert')
            if generated_alert:
                response_parts.append(f"Alert Triggered: YES (Title: '{generated_alert.get('alert_title')}', Severity: '{generated_alert.get('severity')}')")
            else:
                response_parts.append(f"Alert Triggered: No")
            response_parts.append(f"--- Session Ended ---")
        elif self.state.get('status') == 'session_complete':
            response_parts.append(f"\n--- Session Summary ---")
            # Use json.dumps for pretty printing the collected PRO data
            pro_data_summary = json.dumps(self.state.get('pro_data_collected'), indent=2)
            response_parts.append(f"PRO Data Collected:\n{pro_data_summary}")
            response_parts.append(f"--- Proceeding to Analysis ---")

        return "\n\n".join(response_parts)


def main():
    # Initialize Firestore client before starting agents
    initialize_firestore_client()

    # Get patient ID from environment or configuration
    patient_id = os.environ.get("PATIENT_ID", "patient_001")
    logging.info(f"Starting PRO system for patient ID: {patient_id}")

    # Initialize the top-level PRO Workflow Agent
    pro_workflow_agent = PROWorkflowAgent(patient_id=patient_id)

    # Initialize the ADK agent utility
    adk_agent = agent_util.init()

    # The adk_agent.run() method provides an interface for interacting with the agent.
    # It takes a callback function that handles the actual agent logic.
    # The callback receives a 'prompt' (user input string) and returns the agent's response string.
    def agent_callback(prompt: str) -> str:
        # Create a transient AgentState to pass the user's prompt to the workflow agent
        input_state_for_workflow = AgentState(initial_state={'patient_response': prompt})

        # If it's the very first run (no patient_response provided yet, or initial state),
        # trigger the companion agent to start the conversation.
        # This flag ensures the CompanionAgent runs on initial ADK start.
        if not prompt and pro_workflow_agent.state.get('status') == 'ready_to_start':
            input_state_for_workflow.set('initial_trigger', True)

        # Invoke the main workflow agent with the current user input
        # The invoke method will update pro_workflow_agent.state directly.
        # It also returns the formatted string response for the user.
        return pro_workflow_agent.invoke(input_state_for_workflow)

    # Start the agent execution loop
    adk_agent.run(agent_callback)

if __name__ == "__main__":
    main()

