 We will include:
# 1. Agent architecture (CompanionAgent, AdaptiveQuestionnaireAgent, TrendMonitoringAgent)
# 2. FastAPI endpoints
# 3. PostgreSQL schema using SQLAlchemy
# 4. React TypeScript frontend hooks for login and PRO collection

# We'll break this into modular files in the directory structure:
#
# /agents/
#   companion_agent.py
#   adaptive_agent.py
#   trend_monitoring_agent.py
# /db/
#   models.py
#   session.py
# /api/
#   routes.py
# main.py
# /utils/
#   emotional_analysis.py
#   pro_utils.py
# /instructions/
#   companion_instructions.txt
#   adaptive_questionnaire_instructions.txt
#   trend_monitoring_instructions.txt

# FRONTEND:
# /src/hooks/useApi.ts
# /src/pages/Login.tsx
# /src/pages/CheckIn.tsx
# /src/pages/Questionnaire.tsx
# /src/pages/Dashboard.tsx

# AGENT DESCRIPTIONS (from your provided brief):
# ---
# Companion Agent:
#   Role: Initiates conversational check-ins.
#   Logic: Detect emotional state, greet supportively, determine readiness for detailed health conversation.
#
# Adaptive Questionnaire Agent:
#   Role: Asks personalized health questions.
#   Logic: Uses responses and stored data to adapt question tone, complexity, and follow-ups.
#
# Trend Monitoring Agent:
#   Role: Monitors incoming PROs and detects worrisome health patterns over time.
#   Logic: Triggers clinician-ready summaries, risk alerts, and behavioral insight reports.
#
