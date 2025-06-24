
import os
import json
from google.cloud import firestore
import logging
from datetime import datetime # Added for handling SERVER_TIMESTAMP better in logs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Firestore client
db = None

def initialize_firestore_client():
    """Initializes and returns the Firestore client."""
    global db
    if db is None:
        try:
            db = firestore.Client()
            logging.info("Firestore client initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing Firestore client: {e}")
            raise
    return db

def save_state(collection_name: str, document_id: str, state_data: dict):
    """
    Saves agent state data to Firestore.
    Args:
        collection_name: The name of the Firestore collection (e.g., 'agent_states').
        document_id: The ID of the document (e.g., patient_id or agent_id).
        state_data: A dictionary containing the state to save.
    """
    try:
        db_client = initialize_firestore_client()
        doc_ref = db_client.collection(collection_name).document(document_id)
        # Convert any datetime objects to ISO format string before saving, if present
        # This is a general safeguard for complex state data
        cleaned_state_data = {k: v.isoformat() if isinstance(v, datetime) else v for k, v in state_data.items()}
        doc_ref.set(cleaned_state_data)
        logging.info(f"State for {document_id} saved to {collection_name}.")
    except Exception as e:
        logging.error(f"Error saving state for {document_id}: {e}")
        raise

def load_state(collection_name: str, document_id: str) -> dict | None:
    """
    Loads agent state data from Firestore.
    Args:
        collection_name: The name of the Firestore collection.
        document_id: The ID of the document.
    Returns:
        A dictionary containing the loaded state, or None if not found.
    """
    try:
        db_client = initialize_firestore_client()
        doc_ref = db_client.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            state = doc.to_dict()
            logging.info(f"State for {document_id} loaded from {collection_name}.")
            return state
        else:
            logging.info(f"No state found for {document_id} in {collection_name}.")
            return None
    except Exception as e:
        logging.error(f"Error loading state for {document_id}: {e}")
        return None

def save_pro_data(patient_id: str, session_id: str, pro_data: dict):
    """
    Saves Patient Reported Outcome (PRO) data for a specific session to Firestore.
    Organized under patients/{patient_id}/pro_sessions/{session_id}.
    """
    try:
        db_client = initialize_firestore_client()
        doc_ref = db_client.collection('patients').document(patient_id).collection('pro_sessions').document(session_id)
        doc_ref.set(pro_data, merge=True) # Use merge=True to update existing fields or add new ones
        logging.info(f"PRO data for patient {patient_id}, session {session_id} saved.")
    except Exception as e:
        logging.error(f"Error saving PRO data for patient {patient_id}, session {session_id}: {e}")
        raise

def get_all_pro_data_for_patient(patient_id: str) -> list[dict]:
    """
    Retrieves all PRO data sessions for a given patient.
    Returns a list of dictionaries, where each dict is a PRO session.
    """
    try:
        db_client = initialize_firestore_client()
        sessions_ref = db_client.collection('patients').document(patient_id).collection('pro_sessions')
        docs = sessions_ref.stream()
        pro_data_list = []
        for doc in docs:
            pro_data_list.append(doc.to_dict())
        logging.info(f"Retrieved {len(pro_data_list)} PRO sessions for patient {patient_id}.")
        return pro_data_list
    except Exception as e:
        logging.error(f"Error retrieving PRO data for patient {patient_id}: {e}")
        return []

def log_event(event_type: str, patient_id: str, data: dict):
    """
    Logs an event (e.g., alert triggered, session started/ended) to Firestore.
    """
    try:
        db_client = initialize_firestore_client()
        logs_collection = db_client.collection('system_logs')
        log_entry = {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "event_type": event_type,
            "patient_id": patient_id,
            "data": data
        }
        logs_collection.add(log_entry)
        logging.info(f"Logged event: {event_type} for patient {patient_id}.")
    except Exception as e:
        logging.error(f"Error logging event {event_type} for patient {patient_id}: {e}")

