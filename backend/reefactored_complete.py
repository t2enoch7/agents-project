# main.py
import asyncio
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Any # Added Any for generic type hinting
import uuid # For generating session tokens

# Import ADK components
from google.adk.agents import SequentialAgent, Agent # Removed Model import here
# Removed Tool import as it's not directly used for instantiation
# from google.adk.tools import Tool

# FastAPI imports
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer # Although we use custom token, OAuth2 structure is common
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Project specific imports
from agents.companion_agent import CompanionAgent
from agents.adaptive_questionnaire_agent import AdaptiveQuestionnaireAgent
from agents.trend_monitoring_agent import TrendMonitoringAgent
from utils.db_manager import DatabaseManager
from utils.llm_utils import get_gemini_model # Still needed to get the initial LLM instance
from utils.security_utils import anonymize_data, enforce_hipaa_gdpr_owasp

# Import GenerativeModel for type hinting if needed elsewhere, but not from ADK
from google.generativeai import GenerativeModel as GeminiGenerativeModel # Renamed to avoid conflict if Model existed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(title="PRO Multi-Agent System API",
              description="API for collecting, adapting, and analyzing Patient Reported Outcomes using a multi-agent system.")

# Global instances for database and agent runner
db_manager: DatabaseManager = None
runner: 'AgentRunner' = None

# OAuth2PasswordBearer for dependency injection (token based auth)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Pydantic Models for API Request/Response ---
class UserLogin(BaseModel):
    full_name: str
    date_of_birth: str #YYYY-MM-DD format expected

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

class CheckInRequest(BaseModel):
    patient_id: Optional[str] = None # Can be omitted for new check-ins, system generates/links

class CheckInResponse(BaseModel):
    message: str
    patient_id: str
    current_conversation_state: Optional[dict] = None

# --- Dependency to get current user ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retrieves the current authenticated user based on session token."""
    user_data = await db_manager.get_user_by_session_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data

# --- FastAPI Event Handlers ---
@app.on_event("startup")
async def startup_event():
    """Initializes database and agent runner on application startup."""
    global db_manager, runner
    db_manager = DatabaseManager()
    await db_manager.connect()
    runner = AgentRunner(db_manager)
    logger.info("FastAPI application startup completed.")

@app.on_event("shutdown")
async def shutdown_event():
    """Closes database connection on application shutdown."""
    await db_manager.disconnect()
    logger.info("FastAPI application shutdown completed.")

# --- FastAPI Endpoints ---

@app.post("/login", response_model=AuthResponse, summary="User login with full name and date of birth")
async def login_for_access_token(user_data: UserLogin):
    """
    Authenticates a user with full name and date of birth.
    If user exists, returns a session token. If not, creates a new user and token.
    """
    # In a real app, you'd use password hashing and secure user management.
    # For this demo, full_name + DOB serve as a simple 'credential'.
    user = await db_manager.get_user_by_credentials(user_data.full_name, user_data.date_of_birth)

    if not user:
        # If user doesn't exist, create a new user
        logger.info(f"User '{user_data.full_name}' not found. Creating new user.")
        new_user_id = str(uuid.uuid4())
        await db_manager.create_user(new_user_id, user_data.full_name, user_data.date_of_birth)
        user = await db_manager.get_user_by_user_id(new_user_id) # Retrieve the newly created user

    # Create a new session token for the user
    session_token = str(uuid.uuid4())
    await db_manager.create_user_session(user["user_id"], session_token)
    logger.info(f"User '{user_data.full_name}' logged in/created. Session token created.")

    return {"access_token": session_token, "token_type": "bearer", "user_id": user["user_id"]}

@app.post("/api/check_in", response_model=CheckInResponse, summary="Initiate or continue a patient check-in workflow")
async def initiate_patient_check_in(
    request: CheckInRequest,
    current_user: dict = Depends(get_current_user) # Requires authentication
):
    """
    Kicks off or continues the multi-agent PRO check-in workflow for an authenticated user.
    Links the user's ID to a de-identified patient record.
    """
    user_id = current_user["user_id"]

    # In this simplified demo, we link the user_id to a new (or existing) patient_id.
    # The patient_id used for the ADK workflow will be a de-identified ID.
    # For a real system, a user might have multiple patient profiles, or a complex linking logic.

    # For initial check-in, we can generate a consistent patient_id based on user_id
    # for simplicity, or if request.patient_id is provided, use that.
    if request.patient_id:
        patient_id = request.patient_id
        # Ensure the provided patient_id is linked to the current user if it exists
        existing_patient_state = await db_manager.get_patient_state(patient_id)
        if existing_patient_state and existing_patient_state.get('user_id') != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient ID not associated with this user.")
        elif not existing_patient_state:
            # If provided patient_id doesn't exist, we assume it's for this user
            logger.warning(f"Provided patient_id {patient_id} does not exist. Assuming it's for user {user_id} and will create/link.")
            # The run_patient_check_in will handle creation and linking.
    else:
        # If no patient_id is provided, generate a de-identified one linked to user_id
        # For demo, let's use a consistent de-identified ID based on user_id for simplicity.
        # In production, this would be a more robust pseudonymization process.
        patient_id = f"synth_{user_id}"

    logger.info(f"Initiating check-in for user_id: {user_id}, patient_id: {patient_id}")

    try:
        # Pass user_id to the runner so it can be saved with the patient state for linking
        final_state = await runner.run_patient_check_in(patient_id, user_id=user_id)

        # Return only relevant conversation part for frontend display
        latest_agent_response = None
        if final_state.get('conversation_history'):
            for entry in reversed(final_state['conversation_history']):
                if entry.get('role') == 'model':
                    latest_agent_response = entry['parts'][0]['text']
                    break

        return CheckInResponse(
            message="Check-in workflow initiated/continued.",
            patient_id=patient_id,
            current_conversation_state={
                "agent_response": latest_agent_response,
                "emotional_state": final_state.get('emotional_state'),
                "current_agent_status": final_state.get('current_agent_flow_flag')
            }
        )
    except Exception as e:
        logger.error(f"Failed to initiate check-in for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to initiate check-in: {str(e)}")

@app.post("/api/continue_conversation", summary="Continues the conversation within the current agent's context")
async def continue_conversation(
    patient_id: str,
    user_input: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Allows the frontend to send a user's response to the current active agent.
    This simulates a back-and-forth chat.
    """
    user_id = current_user["user_id"]

    # Ensure patient_id is linked to the current user
    patient_state = await db_manager.get_patient_state(patient_id)
    if not patient_state or patient_state.get('user_id') != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient ID not associated with this user or does not exist.")

    # Update patient state with the new user input for the next agent run
    patient_state['latest_patient_input'] = user_input
    # Add user input to conversation history immediately
    if 'conversation_history' not in patient_state:
        patient_state['conversation_history'] = []
    patient_state['conversation_history'].append({"role": "user", "parts": [{"text": user_input}]})
    await db_manager.save_patient_state(patient_state) # Persist the user input

    logger.info(f"Continuing conversation for patient {patient_id} with input: '{user_input}'")

    try:
        # Re-run the SequentialAgent with the updated state.
        final_state = await runner.run_patient_check_in(patient_id, user_id=user_id) # Rerun the entire workflow

        latest_agent_response = None
        if final_state.get('conversation_history'):
            for entry in reversed(final_state['conversation_history']):
                if entry.get('role') == 'model':
                    latest_agent_response = entry['parts'][0]['text']
                    break

        return CheckInResponse(
            message="Conversation continued.",
            patient_id=patient_id,
            current_conversation_state={
                "agent_response": latest_agent_response,
                "emotional_state": final_state.get('emotional_state'),
                "current_agent_status": final_state.get('current_agent_flow_flag')
            }
        )
    except Exception as e:
        logger.error(f"Failed to continue conversation for patient {patient_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to continue conversation: {str(e)}")


# --- AgentRunner remains the same as previous refactoring ---
class AgentRunner:
    """
    Orchestrates the sequential execution of the multi-agent system using
    Google ADK's SequentialAgent and strict ADK Agent instantiation.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # Get the Gemini model instance, this will be passed to ADK Agents
        self.llm_model_instance = get_gemini_model() # This returns the genai.GenerativeModel object

        # Initialize individual sub-agents, passing both the model name for ADK and the instance for generation.
        self.companion_agent = CompanionAgent(
            db_manager=self.db_manager,
            model_name=self.llm_model_instance.model_name, # Pass the string name for ADK Agent's 'model'
            llm_instance=self.llm_model_instance, # Pass the actual LLM instance for generation
        )
        self.adaptive_questionnaire_agent = AdaptiveQuestionnaireAgent(
            db_manager=self.db_manager,
            model_name=self.llm_model_instance.model_name,
            llm_instance=self.llm_model_instance,
        )
        self.trend_monitoring_agent = TrendMonitoringAgent(
            db_manager=self.db_manager,
            model_name=self.llm_model_instance.model_name,
            llm_instance=self.llm_model_instance,
        )

        # Create the root SequentialAgent
        self.root_agent = SequentialAgent(
            name="PROWorkflowPipeline",
            sub_agents=[
                self.companion_agent,
                self.adaptive_questionnaire_agent,
                self.trend_monitoring_agent
            ],
            description="A multi-agent pipeline for collecting, adapting, and analyzing Patient Reported Outcomes.",
        )
        logger.info("AgentRunner initialized with ADK root SequentialAgent.")

    async def run_patient_check_in(self, patient_id: str, user_id: Optional[str] = None):
        """
        Runs the full patient check-in workflow for a given patient using the ADK root agent.
        Includes user_id to link patient state to authenticated user.
        """
        logger.info(f"Starting ADK-orchestrated check-in workflow for patient: {patient_id} (User: {user_id})")

        # 1. Initialize/Load Patient State from PostgreSQL
        patient_state_data = await self.db_manager.get_patient_state(patient_id)
        if not patient_state_data:
            logger.info(f"New patient detected: {patient_id}. Initializing state.")
            initial_state = {
                "patient_id": patient_id,
                "user_id": user_id, # Link user_id here
                "last_check_in": datetime.now() - timedelta(days=7),
                "conversation_history": [],
                "emotional_state": "neutral",
                "language_preference": "en",
                "accessibility_needs": {},
                "pro_intro_statement": "",
                "latest_patient_input": "", # This will be set by the API endpoint if continuing conversation
            }
            await self.db_manager.save_patient_state(initial_state)
            patient_state_data = initial_state
        else:
            logger.info(f"Loaded existing patient state for {patient_id}.")
            # Ensure user_id is updated/linked if it's a new login to existing patient_id
            if user_id and patient_state_data.get('user_id') != user_id:
                patient_state_data['user_id'] = user_id
                await self.db_manager.save_patient_state(patient_state_data) # Persist update

        # Enforce security standards on the state before processing
        patient_state_data = enforce_hipaa_gdpr_owasp(patient_state_data)
        logger.debug(f"Initial patient state for ADK workflow: {patient_state_data}")

        try:
            # The SequentialAgent will pass this state sequentially through its sub_agents.
            final_state = await self.root_agent.run(patient_state_data)
            logger.info(f"SequentialAgent workflow completed for {patient_id}.")

        except Exception as e:
            logger.error(f"Error during SequentialAgent workflow for {patient_id}: {e}", exc_info=True)
            final_state = await self.db_manager.get_patient_state(patient_id) or patient_state_data
            logger.warning(f"Workflow for {patient_id} terminated with an error. Returning last known state.")

        return final_state

# --- Base ADK Agent ---
# agents/base_adk_agent.py (Renamed for clarity, but imported as BaseAgent in sub-agents)
from abc import ABC, abstractmethod
import os
import logging
import json
from typing import Optional, List, Any

from google.adk.agents import Agent # Import the Agent base class

from google.generativeai import GenerativeModel as GeminiGenerativeModel

logger = logging.getLogger(__name__)

class BaseADKAgent(Agent, ABC):
    """
    Abstract base class for all agents in the system, strictly inheriting from Google ADK Agent.
    It handles common initialization, instruction loading, and provides default properties.
    """
    def __init__(
        self,
        db_manager,
        model_adk_name: str, # For ADK Agent's 'model' parameter
        llm_instance: GeminiGenerativeModel, # Our actual LLM instance for generation
        name: str,
        description: str,
        instructions_file: str, # Path to instructions file relative to instructions/
        tools: Optional[List[Any]] = None,
    ):
        # Load instructions from the file first and store them privately
        self._instructions_content: str = self._load_instructions_sync(instructions_file)
        if not self._instructions_content:
            logger.warning(f"Instructions for {name} ({instructions_file}) could not be loaded. Agent might not behave as expected.")

        # Initialize the ADK Agent base class.
        # We explicitly DO NOT pass 'instructions' here to avoid conflicts with ADK's internal Pydantic.
        super().__init__(
            name=name,
            model=model_adk_name,
            description=description,
            tools=tools if tools is not None else [],
        )

        self.db_manager = db_manager
        self._llm_instance = llm_instance # Store our actual LLM instance for use in run() methods
        # The agent_name is no longer a separate field; use self.name directly from ADK Agent base
        self._description = description # Store description for the property

    @property
    def instructions(self) -> str:
        """
        Returns the agent's instructions. This property is now a custom getter
        that provides access to the privately stored instructions content.
        """
        return self._instructions_content

    @property
    def description(self) -> str:
        """Returns the agent's description."""
        return self._description

    @property
    def tools(self) -> List[Any]:
        """Returns a list of tools this agent can use."""
        return super().tools

    @abstractmethod
    async def run(self, state: dict) -> dict:
        """
        Abstract method to be implemented by concrete agents.
        Processes the patient state (an ADK state object) and returns updated state.
        """
        pass

    def _load_instructions_sync(self, filename: str) -> str:
        """Loads agent instructions from the instructions directory (synchronously)."""
        instructions_dir = os.path.join(os.path.dirname(__file__), '..', 'instructions')
        filepath = os.path.join(instructions_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Instruction file not found: {filepath}")
            return ""

# --- Companion Agent ---
# agents/companion_agent.py
import logging
import os
import json
from datetime import datetime
from agents.base_adk_agent import BaseADKAgent
from utils.llm_utils import generate_text_with_gemini
from utils.db_manager import DatabaseManager
from google.generativeai import GenerativeModel as GeminiGenerativeModel
from typing import Optional

logger = logging = logging.getLogger(__name__)

class CompanionAgent(BaseADKAgent):
    """
    Companion Agent initiates conversational check-ins and assesses patient readiness
    for a detailed PRO questionnaire, adhering strictly to ADK Agent structure.
    """
    def __init__(self, db_manager: DatabaseManager, model_name: str, llm_instance: GeminiGenerativeModel):
        self._description = "A friendly AI assistant that initiates conversational check-ins with patients and assesses readiness for detailed PROs."
        self._instructions_file = "companion_instructions.txt"
        super().__init__(
            db_manager=db_manager,
            model_adk_name=model_name, # Pass model_name to BaseADKAgent
            llm_instance=llm_instance, # Pass llm_instance to BaseADKAgent
            name="CompanionAgent",
            description=self._description,
            instructions_file=self._instructions_file, # instructions_file is needed by BaseADKAgent to load content
            tools=[]
        )
        logger.info(f"{self.name} initialized.") # Changed from self.agent_name to self.name

    async def run(self, state: dict) -> dict:
        logger.info(f"{self.name} executing for patient: {state['patient_id']}") # Changed from self.agent_name to self.name

        patient_state = state.copy()
        conversation_history = patient_state.get("conversation_history", [])
        current_emotional_state = patient_state.get("emotional_state", "neutral")
        language_preference = patient_state.get("language_preference", "en")
        accessibility_needs = patient_state.get("accessibility_needs", {})
        latest_patient_input = patient_state.get("latest_patient_input", "")

        if latest_patient_input and (not conversation_history or conversation_history[-1].get("role") != "user"):
            conversation_history.append({"role": "user", "parts": [{"text": latest_patient_input}]})
            patient_state["latest_patient_input"] = ""

        # Use self.instructions directly, which is the custom property in BaseADKAgent
        prompt_text = (
            f"{self.instructions}\n\n" # Uses self.instructions
            f"Patient ID: {patient_state['patient_id']}\n"
            f"Language Preference: {language_preference}\n"
            f"Accessibility Needs: {json.dumps(accessibility_needs)}\n"
            f"Conversation History: {json.dumps(conversation_history[-5:])}\n"
            f"Current Emotional State: {current_emotional_state}\n"
            f"Current Context: Initiate or continue conversation. If patient input was provided: '{latest_patient_input}'\n"
            f"Goal: Gently ascertain readiness for PROs. If patient seems open, suggest moving to specific health questions."
        )

        try:
            response_json_schema = {
                "type": "OBJECT",
                "properties": {
                    "agent_response": {"type": "STRING"},
                    "detected_emotional_state": {"type": "STRING"},
                    "transition_to_adaptive": {"type": "BOOLEAN"},
                    "pro_intro_statement": {"type": "STRING"}
                },
                "required": ["agent_response", "detected_emotional_state", "transition_to_adaptive", "pro_intro_statement"]
            }

            llm_response_str = await generate_text_with_gemini(
                self._llm_instance, # Use the stored llm_instance
                prompt_text,
                response_json_schema
            )
            llm_response = json.loads(llm_response_str)
            agent_response = llm_response["agent_response"]
            new_emotional_state = llm_response["detected_emotional_state"]
            transition_to_adaptive = llm_response["transition_to_adaptive"]
            pro_intro_statement = llm_response["pro_intro_statement"]

        except Exception as e:
            logger.error(f"Error generating {self.name} response for {patient_state['patient_id']}: {e}", exc_info=True) # Changed from self.agent_name to self.name
            agent_response = "I'm sorry, I'm having trouble connecting right now. Can we try again later?"
            new_emotional_state = patient_state.get("emotional_state", "neutral")
            transition_to_adaptive = False
            pro_intro_statement = "Due to a system issue, we cannot proceed with the questionnaire now."

        conversation_history.append({"role": "model", "parts": [{"text": agent_response}]})

        patient_state["conversation_history"] = conversation_history
        patient_state["emotional_state"] = new_emotional_state
        patient_state["last_check_in"] = datetime.now()
        patient_state["pro_intro_statement"] = pro_intro_statement
        patient_state["current_agent_flow_flag"] = "adaptive_questionnaire" if transition_to_adaptive else "companion"

        await self.db_manager.save_patient_state(patient_state)

        return patient_state

# --- Adaptive Questionnaire Agent ---
# agents/adaptive_questionnaire_agent.py
import logging
import os
import json
from datetime import datetime
from agents.base_adk_agent import BaseADKAgent
from utils.llm_utils import generate_text_with_gemini
from utils.db_manager import DatabaseManager
from utils.security_utils import anonymize_data
from google.generativeai import GenerativeModel as GeminiGenerativeModel
from typing import Optional

logger = logging.getLogger(__name__)

class AdaptiveQuestionnaireAgent(BaseADKAgent):
    """
    Adaptive Questionnaire Agent personalizes PRO delivery, adhering strictly to ADK Agent structure.
    """
    def __init__(self, db_manager: DatabaseManager, model_name: str, llm_instance: GeminiGenerativeModel):
        self._description = "An adaptive agent that personalizes and delivers Patient Reported Outcomes questionnaires."
        self._instructions_file = "adaptive_questionnaire_instructions.txt"
        super().__init__(
            db_manager=db_manager,
            model_adk_name=model_name, # Pass model_name to BaseADKAgent
            llm_instance=llm_instance, # Pass llm_instance to BaseADKAgent
            name="AdaptiveQuestionnaireAgent",
            description=self._description,
            instructions_file=self._instructions_file, # instructions_file is needed by BaseADKAgent to load content
            tools=[]
        )
        logger.info(f"{self.name} initialized.") # Changed from self.agent_name to self.name

    async def run(self, state: dict) -> dict:
        logger.info(f"{self.name} executing for patient: {state['patient_id']}") # Changed from self.agent_name to self.name

        patient_state = state.copy()
        conversation_history = patient_state.get("conversation_history", [])
        current_emotional_state = patient_state.get("emotional_state", "neutral")
        language_preference = patient_state.get("language_preference", "en")
        accessibility_needs = patient_state.get("accessibility_needs", {})
        pro_intro_statement = patient_state.get("pro_intro_statement", "")
        latest_patient_input = patient_state.get("latest_patient_input", "")

        if latest_patient_input and (not conversation_history or conversation_history[-1].get("role") != "user"):
            conversation_history.append({"role": "user", "parts": [{"text": latest_patient_input}]})
            patient_state["latest_patient_input"] = ""

        # Use self.instructions directly, which is the custom property in BaseADKAgent
        prompt_text = (
            f"{self.instructions}\n\n" # Uses self.instructions
            f"Patient ID: {patient_state['patient_id']}\n"
            f"Language Preference: {language_preference}\n"
            f"Accessibility Needs: {json.dumps(accessibility_needs)}\n"
            f"Previous PRO Intro Statement (if any): '{pro_intro_statement}'\n"
            f"Conversation History: {json.dumps(conversation_history[-7:])}\n"
            f"Current Emotional State: {current_emotional_state}\n"
            f"Patient's most recent input: '{latest_patient_input}'\n"
            f"Goal: Generate the next adaptive question(s) or conclude and extract PRO data."
        )

        try:
            response_json_schema = {
                "type": "OBJECT",
                "properties": {
                    "agent_question": {"type": "STRING"},
                    "detected_emotional_state": {"type": "STRING"},
                    "pro_data_extracted": {
                        "type": "OBJECT",
                        "properties": {
                            "pain_level": {"type": "INTEGER", "description": "0-10, 0=no pain, 10=worst pain", "nullable": True},
                            "fatigue_level": {"type": "INTEGER", "description": "0-10, 0=no fatigue, 10=extreme fatigue", "nullable": True},
                            "mood_description": {"type": "STRING", "description": "Short description of mood", "nullable": True},
                            "medication_adherence_issue": {"type": "BOOLEAN", "description": "True if issues reported", "nullable": True},
                            "general_wellbeing": {"type": "STRING", "description": "Overall feeling (e.g., good, fair, poor)", "nullable": True}
                        },
                        "description": "De-identified PRO data extracted from conversation, if questionnaire is complete or relevant data is present. Leave empty if not complete."
                    },
                    "is_questionnaire_complete": {"type": "BOOLEAN"}
                },
                "required": ["agent_question", "detected_emotional_state", "pro_data_extracted", "is_questionnaire_complete"]
            }

            llm_response_str = await generate_text_with_gemini(
                self._llm_instance, # Use the stored llm_instance
                prompt_text,
                response_json_schema
            )
            llm_response = json.loads(llm_response_str)
            agent_question = llm_response["agent_question"]
            new_emotional_state = llm_response["detected_emotional_state"]
            pro_data_extracted = llm_response["pro_data_extracted"]
            is_questionnaire_complete = llm_response["is_questionnaire_complete"]

        except Exception as e:
            logger.error(f"Error generating {self.name} response for {patient_state['patient_id']}: {e}", exc_info=True) # Changed from self.agent_name to self.name
            agent_question = "I'm sorry, I'm having a little trouble understanding. Could you please rephrase?"
            new_emotional_state = patient_state.get("emotional_state", "neutral")
            pro_data_extracted = {}
            is_questionnaire_complete = False

        conversation_history.append({"role": "model", "parts": [{"text": agent_question}]})

        patient_state["conversation_history"] = conversation_history
        patient_state["emotional_state"] = new_emotional_state

        pro_data_to_save = None
        if is_questionnaire_complete and pro_data_extracted:
            patient_state["current_agent_flow_flag"] = "trend_monitoring"
            pro_data_to_save = pro_data_extracted
            logger.info(f"{self.name} completing for {patient_state['patient_id']} and recommending transition to Trend Monitoring.") # Changed from self.agent_name to self.name
        else:
            patient_state["current_agent_flow_flag"] = "adaptive_questionnaire"
            logger.info(f"{self.name} continuing for {patient_state['patient_id']}.") # Changed from self.agent_name to self.name

        if pro_data_to_save:
            anonymized_pro_data = anonymize_data(pro_data_to_save)
            await self.db_manager.save_pro_data(patient_state["patient_id"], anonymized_pro_data, self.name) # Changed from self.agent_name to self.name
            patient_state["latest_pro_data_collected"] = anonymized_pro_data

        await self.db_manager.save_patient_state(patient_state)

        return patient_state

# --- Trend Monitoring Agent ---
# agents/trend_monitoring_agent.py
import logging
import os
import json
from datetime import datetime
from agents.base_adk_agent import BaseADKAgent
from utils.llm_utils import generate_text_with_gemini
from utils.db_manager import DatabaseManager
from utils.security_utils import anonymize_data
from google.generativeai import GenerativeModel as GeminiGenerativeModel
from typing import Optional

logger = logging.getLogger(__name__)

class TrendMonitoringAgent(BaseADKAgent):
    """
    Trend Monitoring Agent analyzes historical PRO data for patterns, flags risks,
    and generates summaries/alerts for care teams, adhering strictly to ADK Agent structure.
    """
    def __init__(self, db_manager: DatabaseManager, model_name: str, llm_instance: GeminiGenerativeModel):
        self._description = "An analytical agent that monitors historical PRO data for trends and generates clinical insights and alerts."
        self._instructions_file = "trend_monitoring_instructions.txt"
        super().__init__(
            db_manager=db_manager,
            model_adk_name=model_name, # Pass model_name to BaseADKAgent
            llm_instance=llm_instance, # Pass llm_instance to BaseADKAgent
            name="TrendMonitoringAgent",
            description=self._description,
            instructions_file=self._instructions_file, # instructions_file is needed by BaseADKAgent to load content
            tools=[]
        )
        logger.info(f"{self.name} initialized.") # Changed from self.agent_name to self.name

    async def run(self, state: dict) -> dict:
        logger.info(f"{self.name} executing for patient: {state['patient_id']}") # Changed from self.agent_name to self.name

        patient_state = state.copy()
        patient_id = patient_state["patient_id"]

        historical_pro_data_raw = await self.db_manager.get_pro_data(patient_id)
        historical_pro_data = [anonymize_data(entry["data_elements"]) for entry in historical_pro_data_raw]
        logger.info(f"Fetched {len(historical_pro_data)} historical PRO entries for {patient_id}.")

        # Use self.instructions directly, which is the custom property in BaseADKAgent
        prompt_text = (
            f"{self.instructions}\n\n" # Uses self.instructions
            f"Patient ID: {patient_state['patient_id']}\n"
            f"Historical PRO Data (de-identified): {json.dumps(historical_pro_data, indent=2)}\n"
            f"Goal: Analyze the historical data for trends and potential risk signals. Generate a concise summary and determine if an alert is needed."
        )

        try:
            response_json_schema = {
                "type": "OBJECT",
                "properties": {
                    "alert_type": {"type": "STRING", "enum": ["risk_signal", "trend_summary", "no_alert"], "description": "Type of alert"},
                    "severity": {"type": "STRING", "enum": ["low", "medium", "high", "critical", "none"], "description": "Severity of the alert"},
                    "summary_text": {"type": "STRING", "description": "Concise summary for the care team"}
                },
                "required": ["alert_type", "severity", "summary_text"]
            }

            llm_response_str = await generate_text_with_gemini(
                self._llm_instance, # Use the stored llm_instance
                prompt_text,
                response_json_schema
            )
            llm_response = json.loads(llm_response_str)
            alert_type = llm_response["alert_type"]
            severity = llm_response["severity"]
            summary_text = llm_response["summary_text"]

        except Exception as e:
            logger.error(f"Error generating {self.name} response for {patient_id}: {e}", exc_info=True) # Changed from self.agent_name to self.name
            alert_type = "no_alert"
            severity = "none"
            summary_text = "Automated trend analysis currently unavailable due to a system issue."

        insights_to_save = {
            "alert_type": alert_type,
            "severity": severity,
            "summary_text": summary_text
        }

        await self.db_manager.save_insight_alert(
            patient_id,
            insights_to_save["alert_type"],
            insights_to_save["severity"],
            insights_to_save["summary_text"],
            self.name # Changed from self.agent_name to self.name
        )

        patient_state["current_agent_flow_flag"] = "completed"
        patient_state["last_check_in"] = datetime.now()

        await self.db_manager.save_patient_state(patient_state)

        return patient_state

# --- Database Manager ---
# utils/db_manager.py
import asyncpg
import json
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and operations for PostgreSQL.
    Handles patient state, PRO data, insights/alerts storage, and now user/session management.
    """
    def __init__(self):
        self.conn_pool = None
        self.db_url = os.getenv("DATABASE_URL", "postgresql://user:password@host:5432/dbname")
        logger.info(f"DatabaseManager initialized with URL: {self.db_url.split('@')[-1]}")

    async def connect(self):
        try:
            self.conn_pool = await asyncpg.create_pool(self.db_url)
            logger.info("Successfully connected to PostgreSQL database.")
            await self._init_db_schema()
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.conn_pool = None

    async def disconnect(self):
        if self.conn_pool:
            await self.conn_pool.close()
            logger.info("Disconnected from PostgreSQL database.")

    async def _init_db_schema(self):
        schema_sql = """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Required for gen_random_uuid()

        CREATE TABLE IF NOT EXISTS app_users (
            user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            full_name VARCHAR(255) NOT NULL,
            date_of_birth DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (full_name, date_of_birth) -- Ensure unique users based on these fields
        );

        CREATE TABLE IF NOT EXISTS user_sessions (
            session_token UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES app_users(user_id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour') -- Session expires in 1 hour
        );

        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR(255) PRIMARY KEY, -- This will be the pseudonymized ID, e.g., synth_UUID
            user_id UUID REFERENCES app_users(user_id) ON DELETE SET NULL, -- Link to authenticated user, can be null for non-authenticated PROs
            last_check_in TIMESTAMP,
            current_agent_flow_flag VARCHAR(50),
            conversation_history JSONB,
            emotional_state VARCHAR(50),
            language_preference VARCHAR(10),
            accessibility_needs JSONB,
            pro_intro_statement TEXT,
            latest_patient_input TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pro_data (
            pro_id SERIAL PRIMARY KEY,
            patient_id VARCHAR(255) REFERENCES patients(patient_id),
            data_elements JSONB,
            collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent_source VARCHAR(50)
        );

        CREATE TABLE IF NOT EXISTS insights_alerts (
            alert_id SERIAL PRIMARY KEY,
            patient_id VARCHAR(255) REFERENCES patients(patient_id),
            alert_type VARCHAR(50),
            severity VARCHAR(20),
            summary_text TEXT,
            triggered_by_agent VARCHAR(50),
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_actioned BOOLEAN DEFAULT FALSE,
            actioned_by VARCHAR(255),
            actioned_at TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_patients_last_check_in ON patients(last_check_in);
        CREATE INDEX IF NOT EXISTS idx_pro_data_patient_id ON pro_data(patient_id);
        CREATE INDEX IF NOT EXISTS idx_pro_data_collection_date ON pro_data(collection_date);
        CREATE INDEX IF NOT EXISTS idx_insights_alerts_patient_id ON insights_alerts(patient_id);
        CREATE INDEX IF NOT EXISTS idx_app_users_credentials ON app_users(full_name, date_of_birth);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
        """
        async with self.conn_pool.acquire() as conn:
            await conn.execute(schema_sql)
        logger.info("Database schema initialized.")

    # --- User and Session Management ---
    async def create_user(self, user_id: str, full_name: str, date_of_birth: str) -> bool:
        """Creates a new user."""
        async with self.conn_pool.acquire() as conn:
            try:
                await conn.execute(
                    "INSERT INTO app_users (user_id, full_name, date_of_birth) VALUES ($1, $2, $3::date)",
                    user_id, full_name, date_of_birth
                )
                logger.info(f"User '{full_name}' created with ID: {user_id}")
                return True
            except asyncpg.exceptions.UniqueViolationError:
                logger.warning(f"User with full_name '{full_name}' and DOB '{date_of_birth}' already exists.")
                return False

    async def get_user_by_credentials(self, full_name: str, date_of_birth: str) -> Optional[Dict]:
        """Retrieves a user by full name and date of birth."""
        async with self.conn_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, full_name, date_of_birth FROM app_users WHERE full_name = $1 AND date_of_birth = $2::date",
                full_name, date_of_birth
            )
            return dict(row) if row else None

    async def get_user_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Retrieves a user by user_id."""
        async with self.conn_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, full_name, date_of_birth FROM app_users WHERE user_id = $1",
                user_id
            )
            return dict(row) if row else None

    async def create_user_session(self, user_id: str, session_token: str) -> bool:
        """Creates a new session for a user, expiring in 1 hour."""
        expires_at = datetime.now() + timedelta(hours=1)
        async with self.conn_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO user_sessions (session_token, user_id, expires_at) VALUES ($1, $2, $3)",
                session_token, user_id, expires_at
            )
            logger.info(f"Session created for user {user_id} with token {session_token}")
            return True

    async def get_user_by_session_token(self, session_token: str) -> Optional[Dict]:
        """Retrieves user data associated with a valid session token."""
        async with self.conn_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT au.user_id, au.full_name, au.date_of_birth
                FROM app_users au
                JOIN user_sessions us ON au.user_id = us.user_id
                WHERE us.session_token = $1 AND us.expires_at > CURRENT_TIMESTAMP
                """,
                session_token
            )
            return dict(row) if row else row # Return dict or None

    # --- Existing Patient and PRO Data Management ---
    async def get_patient_state(self, patient_id: str) -> dict | None:
        async with self.conn_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM patients WHERE patient_id = $1", patient_id
            )
            return dict(row) if row else None

    async def save_patient_state(self, state: dict):
        async with self.conn_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO patients (
                    patient_id, user_id, last_check_in, current_agent_flow_flag, conversation_history,
                    emotional_state, language_preference, accessibility_needs,
                    pro_intro_statement, latest_patient_input
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (patient_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    last_check_in = EXCLUDED.last_check_in,
                    current_agent_flow_flag = EXCLUDED.current_agent_flow_flag,
                    conversation_history = EXCLUDED.user_id,
                    emotional_state = EXCLUDED.emotional_state,
                    language_preference = EXCLUDED.language_preference,
                    accessibility_needs = EXCLUDED.accessibility_needs,
                    pro_intro_statement = EXCLUDED.pro_intro_statement,
                    latest_patient_input = EXCLUDED.latest_patient_input,
                    updated_at = CURRENT_TIMESTAMP
                """,
                state["patient_id"],
                state.get("user_id"), # Now includes user_id
                state.get("last_check_in"),
                state.get("current_agent_flow_flag"),
                json.dumps(state.get("conversation_history", [])),
                state.get("emotional_state"),
                state.get("language_preference"),
                json.dumps(state.get("accessibility_needs", {})),
                state.get("pro_intro_statement"),
                state.get("latest_patient_input")
            )
        logger.debug(f"Patient state saved for {state['patient_id']}")

    async def save_pro_data(self, patient_id: str, data_elements: dict, agent_source: str):
        async with self.conn_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO pro_data (patient_id, data_elements, agent_source)
                VALUES ($1, $2, $3)
                """,
                patient_id,
                json.dumps(data_elements),
                agent_source
            )
        logger.debug(f"PRO data saved for {patient_id}")

    async def get_pro_data(self, patient_id: str) -> list[dict]:
        async with self.conn_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM pro_data WHERE patient_id = $1 ORDER BY collection_date ASC", patient_id
            )
            return [dict(row) for row in rows]

    async def save_insight_alert(self, patient_id: str, alert_type: str, severity: str, summary_text: str, triggered_by_agent: str):
        async with self.conn_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO insights_alerts (patient_id, alert_type, severity, summary_text, triggered_by_agent)
                VALUES ($1, $2, $3, $4, $5)
                """,
                patient_id,
                alert_type,
                severity,
                summary_text,
                triggered_by_agent
            )
        logger.debug(f"Insight/Alert saved for {patient_id}: {alert_type}")

    async def get_insights_alerts(self, patient_id: str) -> list[dict]:
        async with self.conn_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM insights_alerts WHERE patient_id = $1 ORDER BY triggered_at DESC", patient_id
            )
            return [dict(row) for row in rows]


# --- LLM Utilities ---
# utils/llm_utils.py
import google.generativeai as genai
import os
import json
import logging
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

def get_gemini_model():
    """
    Initializes and returns the Gemini Flash model instance from google.generativeai.
    Prioritizes Google Cloud default credentials (e.g., Service Account via GOOGLE_APPLICATION_CREDENTIALS)
    then falls back to GOOGLE_API_KEY.
    """
    try:
        genai.configure()
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Gemini-2.0-flash model initialized using Google Cloud default credentials.")
        return model
    except (DefaultCredentialsError, Exception) as e:
        logger.warning(f"Could not initialize Gemini model with default credentials: {e}. Falling back to GOOGLE_API_KEY.")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Neither GOOGLE_APPLICATION_CREDENTIALS nor GOOGLE_API_KEY environment variable set.")
            raise ValueError("Authentication credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_API_KEY in your .env file.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Gemini-2.0-flash model initialized using GOOGLE_API_KEY.")
        return model

async def generate_text_with_gemini(model, prompt_text: str, response_json_schema: dict = None) -> str:
    """
    Generates text using the Gemini model instance, optionally enforcing a JSON schema for output.
    This function wraps the raw generativeai call for structured output.
    """
    try:
        if response_json_schema:
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": response_json_schema
            }
            logger.debug(f"Generating with JSON schema: {json.dumps(response_json_schema)}")
            response = await model.generate_content_async(
                prompt_text,
                generation_config=generation_config
            )
        else:
            response = await model.generate_content_async(prompt_text)

        if response.candidates and response.candidates[0].content.parts:
            generated_content = response.candidates[0].content.parts[0].text
            logger.debug(f"LLM generated content: {generated_content[:100]}...")
            return generated_content
        else:
            logger.warning(f"Gemini API returned no candidates or content parts for prompt: {prompt_text[:50]}...")
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                logger.warning(f"Prompt blocked: {response.prompt_feedback.block_reason}")
            return json.dumps({"error": "No content generated or blocked by safety filters."})

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        return json.dumps({"error": f"LLM generation failed: {str(e)}"})


# --- Security Utilities remains unchanged ---
# utils/security_utils.py
import json
import logging

logger = logging.getLogger(__name__)

def anonymize_data(data: dict) -> dict:
    """
    Anonymizes or de-identifies sensitive patient data.
    This is a placeholder for a robust de-identification process.
    For a prototype, it removes or generalizes certain fields.
    """
    anonymized = data.copy()
    logger.debug("Data anonymization placeholder executed.")
    return anonymized

def enforce_hipaa_gdpr_owasp(patient_state: dict) -> dict:
    """
    Placeholder function to signify adherence to HIPAA, GDPR, and OWASP principles.
    For this prototype, it mostly acts as a reminder that these are critical.
    It can ensure that patient_id in the *application logic* is a pseudonym.
    """
    if 'patient_id' in patient_state and not patient_state['patient_id'].startswith("synth_"):
        patient_state['patient_id'] = f"synth_{patient_state['patient_id']}"
        logger.warning(f"Patient ID {patient_state['patient_id']} was not synthetic. Pseudonymized for prototype.")

    logger.info("HIPAA, GDPR, OWASP security enforcement placeholder executed. No direct sensitive data processed here.")
    return patient_state

# --- Instructions files remain unchanged ---
# instructions/companion_instructions.txt
"""
You are the Companion Agent, a friendly and empathetic AI assistant designed to initiate
conversational check-ins with patients managing chronic conditions. Your primary goal
is to engage the patient in a natural, supportive conversation, adapt to their emotional state,
and subtly assess their readiness to discuss their health in more detail (i.e., proceed to a PRO questionnaire).

**Your Persona:**
- Empathetic and caring.
- Conversational and natural, avoiding overly clinical language initially.
- Patient and reassuring.
- Aware of and adaptable to patient's language and accessibility needs.

**Your Tasks:**
1.  **Initiate Check-in:** Start with a warm, open-ended greeting.
2.  **Adapt Tone/Complexity:** Adjust your language and complexity based on inferred comprehension and historical interaction patterns.
3.  **Detect Emotional Cues:** Pay close attention to keywords, tone (if audio input were available), and sentiment to detect emotional states (e.g., tired, sad, anxious, frustrated, positive). Respond with empathy and reassurance as appropriate.
4.  **Guide Conversation:** Gently steer the conversation towards general well-being and health without being intrusive.
5.  **Assess Readiness for PROs:** Determine if the patient seems open and willing to discuss specific health aspects. If they express any discomfort or resistance, do not push them. Instead, offer reassurance and suggest connecting later or providing general well-being tips.
6.  **Transition Decision:** Based on the conversation, decide whether to transition the patient to the "Adaptive Questionnaire Agent" or continue the conversation as the Companion Agent.

**Output Format (JSON):**
You must output a JSON object with the following keys:
- `agent_response`: The conversational text you will send back to the patient.
- `detected_emotional_state`: Your assessment of the patient's current emotional state (e.g., "neutral", "happy", "tired", "anxious", "frustrated", "sad").
- `transition_to_adaptive`: A boolean (true/false) indicating if the patient should now be transitioned to the Adaptive Questionnaire Agent. Set to `true` if they express readiness or a clear opening to discuss symptoms/well-being.
- `pro_intro_statement`: A brief, gentle statement to introduce the idea of more specific health questions, to be used if `transition_to_adaptive` is true. Example: "If you're comfortable, I have a few specific questions about how you've been feeling that might help your care team."
"""

# instructions/adaptive_questionnaire_instructions.txt
"""
You are the Adaptive Questionnaire Agent. Your role is to conduct a personalized and adaptive
Patient Reported Outcomes (PRO) questionnaire. You receive the patient after the Companion Agent
has established rapport. Your goal is to efficiently and empathetically collect structured PRO data.

**Your Persona:**
- Focused and clear.
- Empathetic and understanding, especially when dealing with sensitive health topics.
- Adaptive and intelligent, adjusting questions based on responses.
- Respectful of patient privacy and comfort.

**Your Tasks:**
1.  **Acknowledge Transition:** Start by smoothly transitioning from the Companion Agent's last statement, potentially using the `pro_intro_statement` provided by the Companion Agent.
2.  **Generate Adaptive Questions:** Based on the patient's conversation history, previous responses, and detected emotional cues, generate the *next logical question* to gather specific PRO data. Avoid redundant questions.
    - Examples of PRO data points to collect (but adapt and expand): pain levels (0-10), fatigue levels (0-10), mood, sleep quality, medication adherence issues, general well-being.
3.  **Detect Emotional Cues (Continued):** Continue to monitor and adapt to the patient's emotional state throughout the questionnaire. Offer reassurance or simplify questions if they appear distressed or confused.
4.  **Validate and Clarify:** If a response is ambiguous, ask clarifying questions.
5.  **Data Extraction:** Once a piece of PRO data is clearly expressed (e.g., "My pain is about a 7," "I'm feeling very tired"), extract it into a structured JSON format.
6.  **Determine Completion:** Decide if enough core PRO data has been collected to conclude the questionnaire. It's better to get key data points than to exhaust the patient.
7.  **Transition to Trend Monitoring:** If the questionnaire is deemed complete, signal the transition to the "Trend Monitoring Agent" and provide the extracted PRO data.

**Output Format (JSON):
You must output a JSON object with the following keys:
- `agent_question`: The next question or concluding statement you will send to the patient.
- `detected_emotional_state`: Your assessment of the patient's current emotional state (e.g., "neutral", "happy", "tired", "anxious", "frustrated", "sad").
- `pro_data_extracted`: A JSON object containing *de-identified* PRO data points extracted so far.
  - Keys should be general categories (e.g., `pain_level`, `fatigue_level`, `mood_description`, `medication_adherence_issue`, `general_wellbeing`).
  - Values should be appropriate data types (e.g., integer for level, string for description, boolean).
  - This object should be populated only when relevant data is present.
"""
