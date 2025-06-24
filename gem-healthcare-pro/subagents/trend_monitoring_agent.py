# subagents/trend_monitoring_agent.py

import logging
import json
from google.generative_agent import AgentState
from google.adk.agents import LlmAgent, SequentialAgent # New imports
import google.generativeai as genai
from utils.firestore_utils import get_all_pro_data_for_patient, log_event, save_pro_data
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrendMonitoringPhaseAgent: # Renamed for clarity
    """
    The Trend Monitoring Phase Agent detects concerning patterns in PRO data over time.
    It takes an AgentState, retrieves historical data, performs analysis, and
    updates the state with analysis results and potential alerts.
    """

    def __init__(self, model_config: dict = None):
        self.model_config = model_config if model_config is not None else {'temperature': 0.3}

        self.analysis_llm = LlmAgent(
            name="TrendAnalysisLLM",
            instruction=(
                "You are a healthcare data analyst AI. Analyze the patient-reported outcomes (PRO) data "
                "provided in 'all_pro_data' and 'new_pro_session_data_with_timestamp'. "
                "Identify any concerning trends or risk signals based on changes over time (e.g., worsening pain, decreased activity, changes in emotional state). "
                "Generate a concise summary of the patient's current status and identified trends. "
                "If a significant concern is detected (e.g., pain score increase by 3 points, sustained low energy), recommend an alert for the care team. "
                "Output in JSON format with 'summary' (string) and 'risk_signals' (list of strings, or empty list if none), and 'alert_recommendation' (boolean). "
                "Store this JSON in 'analysis_result'."
            ),
            output_key="analysis_result",
            model_name='gemini-1.5-flash',
            generation_config={'response_mime_type': 'application/json', **self.model_config}
        )

        self.alert_generation_llm = LlmAgent(
            name="AlertGenerationLLM",
            instruction=(
                "Based on the PRO analysis result in 'analysis_result', draft a concise, actionable smart alert "
                "for a healthcare care team if 'alert_recommendation' is true. "
                "Include the patient ID from 'patient_id', a brief summary of the concern, "
                "and any specific data points supporting the alert. "
                "Format as JSON with 'patient_id', 'alert_title', 'alert_description', 'severity' (Low, Medium, High). "
                "Output the JSON to 'generated_alert_data'. If no alert is recommended, output an empty dictionary or a specific indicator."
            ),
            output_key="generated_alert_data",
            model_name='gemini-1.5-flash',
            generation_config={'response_mime_type': 'application/json', **self.model_config}
        )

        self.trend_pipeline = SequentialAgent(
            name="TrendMonitoringPipeline",
            sub_agents=[
                self.analysis_llm,
                self.alert_generation_llm
            ]
        )
        logging.info("TrendMonitoringPhaseAgent initialized.")

    def invoke(self, state: AgentState):
        """
        Invokes the Trend Monitoring Agent's logic, updating the shared AgentState.
        Args:
            state: The current AgentState for the patient's PRO journey.
                   Expected to contain: 'patient_id', 'session_id', 'pro_data_collected' (new data).
                   Will update 'analysis_summary', 'risk_signals_detected', 'generated_alert',
                   'last_analysis_timestamp', 'alerts_triggered_history', 'current_agent_phase'.
        """
        patient_id = state.get('patient_id')
        session_id = state.get('session_id')
        new_pro_session_data = state.get('pro_data_collected')

        if not patient_id or not session_id or not new_pro_session_data:
            logging.error("TrendMonitoringPhaseAgent requires patient_id, session_id, and pro_data_collected in AgentState.")
            state.set('error_message', "Trend analysis error: Missing required data.")
            state.set('current_agent_phase', 'completed') # End flow
            return

        # Add timestamp to the new PRO data for historical context
        new_pro_session_data['timestamp'] = datetime.now().isoformat()
        state.set('new_pro_session_data_with_timestamp', new_pro_session_data) # Store in state for LLM

        log_event("TrendAgent_invoke", patient_id, {
            "session_id": session_id,
            "new_pro_data_summary": new_pro_session_data
        })

        # Save the new PRO data session to long-term storage
        # This is done *before* full analysis, so it's part of the patient's record
        save_pro_data(patient_id, session_id, new_pro_session_data)

        # Retrieve all historical PRO data for this patient
        all_pro_data = get_all_pro_data_for_patient(patient_id)
        state.set('all_pro_data', all_pro_data) # Store in state for LLM

        # Invoke the sequential pipeline for analysis and alert generation
        try:
            logging.info(f"TrendMonitoringAgent invoking internal trend pipeline for patient {patient_id}.")
            self.trend_pipeline.invoke(state) # The pipeline operates on the main state
        except Exception as e:
            logging.error(f"Error invoking trend analysis pipeline for patient {patient_id}: {e}")
            state.set('analysis_summary', "Error during trend analysis.")
            state.set('risk_signals_detected', ["Analysis failed"])
            state.set('generated_alert', None)
            state.set('current_agent_phase', 'completed') # End flow
            return

        # Retrieve results from the state after pipeline execution
        analysis_result = state.get('analysis_result', {})
        smart_alert = state.get('generated_alert_data')

        state.set('analysis_summary', analysis_result.get('summary', 'N/A'))
        state.set('risk_signals_detected', analysis_result.get('risk_signals', []))
        state.set('generated_alert', smart_alert if smart_alert and analysis_result.get('alert_recommendation') else None)

        if smart_alert and analysis_result.get('alert_recommendation'):
            alerts_history = state.get('alerts_triggered_history', [])
            alerts_history.append({
                'timestamp': datetime.now().isoformat(),
                'alert': smart_alert
            })
            state.set('alerts_triggered_history', alerts_history)
            log_event("TrendAgent_alert_triggered", patient_id, smart_alert)

        state.set('last_analysis_timestamp', datetime.now().isoformat())
        state.set('current_agent_phase', 'completed') # Mark flow as completed for this turn
        state.set('status', 'analysis_complete')

        logging.info(f"TrendMonitoringPhaseAgent completed analysis for patient {patient_id}.")

