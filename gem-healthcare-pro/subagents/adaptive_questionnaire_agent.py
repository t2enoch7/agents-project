# subagents/adaptive_questionnaire_agent.py

import logging
import json
from google.generative_agent import AgentState
from google.adk.agents import LlmAgent, SequentialAgent
import google.generativeai as genai
from utils.firestore_utils import save_pro_data, log_event # Removed state save/load as it's handled by main orchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdaptiveQuestionnairePhaseAgent: # Renamed for clarity
    """
    The Adaptive Questionnaire Phase Agent personalizes PRO data collection.
    It takes an AgentState, processes patient input, adapts questions, and
    updates the PRO data within the state. It uses internal ADK agents.
    """

    def __init__(self, model_config: dict = None):
        self.model_config = model_config if model_config is not None else {'temperature': 0.7}

        # Define internal LlmAgents for specific tasks within the adaptive flow
        self.emotion_detector_llm = LlmAgent(
            name="EmotionDetectorLLM",
            instruction=(
                "Analyze the patient response provided in 'patient_response' for emotional cues. "
                "Respond with a single word representing the primary emotion or 'neutral' if none is strong. "
                "Examples: 'stressed', 'sad', 'frustrated', 'optimistic', 'calm'. "
                "Output the result to 'detected_emotional_state'." # Changed key for clarity
            ),
            input_key="patient_response",
            output_key="detected_emotional_state",
            model_name='gemini-1.5-flash',
            generation_config=self.model_config
        )

        self.pro_response_parser_llm = LlmAgent(
            name="PROResponseParserLLM",
            instruction=(
                "You are a data parser. Extract key health data from the patient's response "
                "found in 'patient_response' to the given question in 'last_question_text'. " # Changed key
                "Provide a JSON object with relevant fields. "
                "For pain, use 'pain_level' (0-10 integer). For energy, use 'energy_change' (text description). "
                "For daily impact, use 'daily_impact' (text description). "
                "If a numerical scale is mentioned, extract it. Prioritize quantitative data if available. "
                "Output the JSON object to 'parsed_pro_data'." # Changed key
            ),
            output_key="parsed_pro_data",
            model_name='gemini-1.5-flash',
            generation_config={'response_mime_type': 'application/json', **self.model_config}
        )

        self.question_adapter_llm = LlmAgent(
            name="QuestionAdapterLLM",
            instruction=(
                "Adapt the original question found in 'original_question_text' for a healthcare questionnaire. " # Changed key
                "Consider the 'current_tone', 'current_complexity', and 'detected_emotional_state' (of the patient). "
                "If a previous 'patient_response' is available, use it to generate a follow-up, ensuring the response is concise and encourages further PRO data collection. "
                "If the patient's 'detected_emotional_state' indicates a negative emotion, offer reassurance before adapting the question. "
                "Output the adapted question to 'adapted_question_text'." # Changed key
            ),
            output_key="adapted_question_text",
            model_name='gemini-1.5-flash',
            generation_config=self.model_config
        )

        # The sequential pipeline for processing a patient's response and preparing for the next question.
        self.processing_pipeline = SequentialAgent(
            name="AdaptivePROProcessingPipeline",
            sub_agents=[
                self.emotion_detector_llm,
                self.pro_response_parser_llm,
                self.question_adapter_llm
            ]
        )
        logging.info("AdaptiveQuestionnairePhaseAgent initialized.")

    def _define_initial_question_flow(self):
        """Defines a set of initial, generic PRO questions."""
        return [
            "How would you describe your overall pain level today on a scale of 0 to 10, where 0 is no pain and 10 is the worst pain imaginable?",
            "Have you experienced any changes in your energy levels recently? If so, what kind of changes?",
            "How has your chronic condition impacted your daily activities and quality of life over the past week?",
            "Are there any specific symptoms or concerns you'd like to share that are bothering you today?",
            "On a scale of 0 to 10, how well do you feel you are managing your condition today?"
        ]

    def invoke(self, state: AgentState):
        """
        Invokes the Adaptive Questionnaire Agent's logic, updating the shared AgentState.
        Args:
            state: The current AgentState for the patient's PRO journey.
                   Expected to contain: 'patient_id', 'session_id', 'patient_response' (if any),
                   'current_question_index', 'questions_asked_count', 'pro_data_collected',
                   'conversation_history', 'current_tone', 'current_complexity'.
                   Will update these and 'agent_response', 'current_agent_phase', 'status'.
        """
        patient_id = state.get('patient_id')
        session_id = state.get('session_id')
        patient_response = state.get('patient_response') # User input for this turn

        log_event("AdaptiveAgent_invoke", patient_id, {
            "session_id": session_id,
            "patient_response": patient_response,
            "current_question_index": state.get('current_question_index')
        })

        # Get and update core state variables
        conversation_history = state.get('conversation_history', [])
        pro_data_collected = state.get('pro_data_collected', {})
        current_question_index = state.get('current_question_index', 0)
        questions_asked_count = state.get('questions_asked_count', 0)
        max_questions_per_session = state.get('max_questions_per_session', 5) # Default if not set in orchestrator

        question_flow = state.get('question_flow', self._define_initial_question_flow())
        state.set('question_flow', question_flow) # Ensure question_flow is in state for next calls

        # Append patient response to history
        if patient_response:
            conversation_history.append({'role': 'user', 'text': patient_response})
            state.set('conversation_history', conversation_history) # Update state

        # Prepare state for the internal processing pipeline
        pipeline_input_state = AgentState(initial_state={
            'patient_response': patient_response,
            'current_tone': state.get('current_tone', 'supportive'),
            'current_complexity': state.get('current_complexity', 'simple')
        })

        # Process previous question's response if applicable
        if patient_response and current_question_index > 0 and questions_asked_count > 0:
            last_question = question_flow[current_question_index - 1]
            pipeline_input_state.set('last_question_text', last_question) # For the parser

        # Set the 'original_question_text' for the adapter for the *next* question
        question_to_ask = None
        if questions_asked_count < max_questions_per_session and \
           current_question_index < len(question_flow):
            question_to_ask = question_flow[current_question_index]
            pipeline_input_state.set('original_question_text', question_to_ask)

        # --- Execute the internal sequential processing pipeline ---
        if patient_response or state.get('initial_trigger', False): # Run pipeline if input or initial trigger
            try:
                logging.info(f"AdaptiveAgent invoking internal processing pipeline for patient {patient_id}.")
                self.processing_pipeline.invoke(pipeline_input_state)
            except Exception as e:
                logging.error(f"Error invoking internal processing pipeline for patient {patient_id}: {e}")
                state.set('agent_response', "I'm sorry, I encountered an issue processing your response. Please try again.")
                state.set('status', 'error')
                return

        # Retrieve results from the pipeline_input_state and update the main state
        state.set('emotional_state', pipeline_input_state.get('detected_emotional_state', state.get('emotional_state', 'neutral')))

        parsed_data = pipeline_input_state.get('parsed_pro_data')
        if parsed_data and isinstance(parsed_data, dict):
            if any(parsed_data.values()):
                pro_data_collected.update(parsed_data)
                state.set('pro_data_collected', pro_data_collected)
                logging.info(f"PRO data updated for session {session_id}: {pro_data_collected}")

        adapted_question_text = pipeline_input_state.get('adapted_question_text', question_to_ask)


        # Logic to ask next question or complete session
        if questions_asked_count < max_questions_per_session:
            if question_to_ask:
                conversation_history.append({'role': 'assistant', 'text': adapted_question_text})
                state.set('conversation_history', conversation_history)

                state.set('current_question_index', current_question_index + 1)
                state.set('questions_asked_count', questions_asked_count + 1)

                state.set('agent_response', adapted_question_text)
                state.set('status', 'ask_question')
                state.set('current_agent_phase', 'adaptive_questionnaire_agent') # Stay in this phase
                logging.info(f"AdaptiveAgent asking question {state.get('current_question_index')} for patient {patient_id}.")
            else:
                # All predefined questions asked, but max_questions_per_session not reached (no more questions to pull)
                logging.info(f"AdaptiveAgent completed predefined questions for patient {patient_id}, session {session_id}.")
                self._complete_session(state, patient_id, session_id, pro_data_collected)
        else:
            # Max questions reached, end session
            self._complete_session(state, patient_id, session_id, pro_data_collected)

    def _complete_session(self, state: AgentState, patient_id: str, session_id: str, pro_data_collected: dict):
        """Helper to mark session complete and transition."""
        save_pro_data(patient_id, session_id, pro_data_collected)
        log_event("AdaptiveAgent_session_complete", patient_id, {
            "session_id": session_id,
            "pro_data_summary": pro_data_collected
        })
        state.set('agent_response', "Thank you for completing the check-in! Your responses are valuable.")
        state.set('status', 'session_complete')
        state.set('current_agent_phase', 'trend_monitoring_agent') # Handoff to Trend Monitoring
        logging.info(f"AdaptiveAgent completed session for patient {patient_id}, session {session_id}. Handing off to Trend Monitoring.")

