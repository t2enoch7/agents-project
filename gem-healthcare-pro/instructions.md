Step-by-Step Setup and Run Instructions for PRO Multi-Agent System
This guide will walk you through setting up and running the Patient Reported Outcomes (PRO) multi-agent system using the Google Agent Development Kit (ADK) and Google Cloud Firestore.

1. Prerequisites
Before you begin, ensure you have the following:

Python 3.9+: Installed on your system.

pip: Python package installer (usually comes with Python).

Google Cloud Account: With billing enabled.

Google Cloud Project: Create a new project or use an existing one.

Google Cloud SDK (gcloud CLI): Installed and authenticated on your machine.

Run gcloud init and gcloud auth application-default login to set up your credentials.

Environment Variables:

GOOGLE_APPLICATION_CREDENTIALS: Path to your service account key file (if running locally outside a GCP environment).

PATIENT_ID: (Optional) The patient ID you want to use for testing. Defaults to patient_001 if not set.

2. Google Cloud Project Setup
Enable APIs: In your Google Cloud Project, enable the following APIs:

Cloud Firestore API

Generative Language API

Cloud Logging API

You can do this via the Google Cloud Console: Navigate to "APIs & Services" > "Enabled APIs & Services" and click "Enable APIs and Services". Search for each API and enable it.

Firestore Database Setup:

Go to Firestore in the Google Cloud Console.

Choose a database location (e.g., nam5 for North America, europe-west1 for Europe).

Select Native mode for the database.

You do not need to create any collections manually; the application will create them as needed (companion_agent_states, adaptive_agent_states, trend_agent_states, patients, system_logs, pro_workflow_states).

Service Account (for Local Development):

If you're testing locally (not deploying directly via ADK CLI's full deployment), you'll need a service account.

Go to IAM & Admin > Service Accounts.

Create a new service account.

Grant it the following roles:

Cloud Datastore User (or Cloud Firestore User)

Logs Writer

Service Usage Consumer (for invoking Generative Language API)

Create a JSON key for this service account and download it.

Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the absolute path of this JSON key file.

On Linux/macOS: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"

On Windows (Command Prompt): set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\keyfile.json"

On Windows (PowerShell): $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\keyfile.json"

3. Project Structure
Create the following directory and file structure:

pro_system/
├── main.py
├── requirements.txt
├── utils/
│   └── firestore_utils.py
└── subagents/
    ├── __init__.py
    ├── companion_agent.py
    ├── adaptive_questionnaire_agent.py
    └── trend_monitoring_agent.py

4. Populate Files
Copy the provided code into the respective files:

requirements.txt:

google-generative-ai
google-generative-agent
google-cloud-firestore
google-cloud-logging

utils/firestore_utils.py: (Use the code from the previous response)

subagents/companion_agent.py: (Use the code from the companion_agent_refactor immersive)

subagents/adaptive_questionnaire_agent.py: (Use the code from the adaptive_questionnaire_agent_refactor immersive)

subagents/trend_monitoring_agent.py: (Use the code from the trend_monitoring_agent_refactor immersive)

main.py: (Use the code from the main_py_refactor immersive)

subagents/__init__.py: (Create an empty file to make subagents a Python package)

5. Install Python Dependencies
Navigate to the pro_system directory in your terminal and run:

pip install -r requirements.txt

6. Run the Solution
You can run this solution using the ADK development server or deploy it fully.

Option A: Running with ADK Development Server (Recommended for Testing)
Navigate to the pro_system directory in your terminal.

Run the ADK development server:

adk serve main.py

The output will provide a URL (usually http://localhost:8080). Open this URL in your web browser.

The ADK Web UI will load, showing a chat interface.

Option B: Deploying with ADK (More involved, follow ADK documentation)
For full deployment, refer to the official Google Agent Development Kit documentation on how to deploy agents. This typically involves configuring adk.yaml and running adk deploy.

7. Interact with the System in ADK Web
Once the ADK Web UI is open:

Initial Greeting: The PROWorkflowAgent will automatically start and trigger the CompanionPhaseAgent. You should see an initial greeting like:

System: Hello! How are you feeling today?

Provide Patient Response: Type your response in the input box (e.g., "I'm feeling a bit tired today and have some back pain.") and press Enter.

Adaptive Questionnaire: The system will transition to the AdaptiveQuestionnairePhaseAgent. It will process your input (detect emotion, parse data implicitly) and ask the first adaptive question.

Continue the Conversation: Keep responding to the questions. The agent will adapt its tone and questions based on your answers.

Session Completion: After a few questions (defaults to 5, set by max_questions_per_session in main.py), the AdaptiveQuestionnairePhaseAgent will mark the session as complete.

Trend Monitoring: The system will then automatically hand off to the TrendMonitoringPhaseAgent. This agent will analyze all historical PRO data for the patient (including the just-completed session) and provide a summary, risk signals, and potentially an alert.
You will see output similar to this:

System: Thank you for completing the check-in! Your responses are valuable.

--- Trend Analysis ---
Summary: Patient reports...
Risk Signals: [list of signals or None]
Alert Triggered: YES/NO (details if yes)
--- Session Ended ---

8. Verify Data in Firestore
While the agent is running and you are interacting:

Go to your Google Cloud Console.

Navigate to Firestore > Data.

You should see collections created:

pro_workflow_states: Contains the overall state of your patient's PRO journey (updated after each turn).

patients: This collection will contain sub-collections pro_sessions for each patient, storing the structured PRO data from each completed session.

system_logs: Contains logs of agent calls and events.

This comprehensive guide should enable you to successfully set up, run, and test your multi-agent PRO system.
