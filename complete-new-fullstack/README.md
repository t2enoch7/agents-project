# Patient Reported Outcomes Multi-Agent System

A sophisticated multi-agent system for collecting and analyzing Patient Reported Outcomes (PROs) using Google AI SDK, Gemini 2.0 Pro, FastAPI, and SQLite. The system provides a patient-centered, clinician-ready feedback loop through three coordinated AI agents.

## 🏥 System Overview

This system addresses healthcare challenges in capturing high-quality PROs for chronic care patients by providing:

- **Conversational check-ins** with emotional intelligence
- **Adaptive questionnaires** that personalize based on patient responses
- **Trend monitoring** with real-time clinical insights and alerts
- **Multilingual and accessibility support**
- **Compliance with data privacy standards**

## 🤖 Multi-Agent Architecture

### 1. Companion Agent

- **Purpose**: Initiates conversational check-ins and builds rapport
- **Capabilities**:
  - Emotional state detection and response adaptation
  - Multilingual communication support
  - Accessibility-aware interactions
  - Trust-building through empathetic communication

### 2. Adaptive Questionnaire Agent

- **Purpose**: Delivers personalized PRO collection
- **Capabilities**:
  - Dynamic question complexity adjustment
  - Comprehension monitoring and clarification
  - Response quality assessment
  - Condition-specific question templates

### 3. Trend Monitoring Agent

- **Purpose**: Analyzes patterns and generates clinical insights
- **Capabilities**:
  - Time-series pattern recognition
  - Risk assessment and alert generation
  - Clinical recommendation generation
  - Predictive analysis for early intervention

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google AI API key (for Gemini 2.0 Pro)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd healhcare-pro
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

```bash
# Create .env file
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

4. **Run the system**

```bash
# Start the FastAPI server
uvicorn main:app --reload

# Or test the workflow without external dependencies
python simple_test.py
```

## 📋 API Endpoints

### Authentication

- `POST /auth/login` - Login with email and date of birth

### Patient Management

- `POST /patients` - Create/update patient profile
- `GET /patients/{patient_id}` - Get patient information

### Multi-Agent Conversation

- `POST /conversation/start` - Start conversation with companion agent
- `POST /conversation/continue` - Continue conversation with adaptive agents
- `POST /conversation/analyze` - Analyze trends and generate insights
- `POST /conversation/complete` - Complete session with final insights

### System

- `GET /health` - Health check endpoint

## 🔄 Workflow Example

### 1. Patient Login

```json
POST /auth/login
{
  "email": "john.doe@example.com",
  "date_of_birth": "1985-03-15"
}
```

### 2. Start Conversation

```json
POST /conversation/start?token=<token>
Response:
{
  "session_id": "uuid",
  "response": "Hello! How are you feeling today?",
  "agent_type": "companion"
}
```

### 3. Continue Conversation

```json
POST /conversation/continue?token=<token>
{
  "message": "I'm feeling tired and my blood sugar is high",
  "session_id": "uuid"
}
```

### 4. Get Insights

```json
POST /conversation/analyze?token=<token>
Response:
{
  "risk_score": 0.6,
  "alerts": [...],
  "recommendations": [...]
}
```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Companion     │    │   Adaptive       │    │   Trend         │
│     Agent       │    │  Questionnaire   │    │   Monitoring    │
│                 │    │     Agent        │    │     Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   Backend       │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SQLite        │
                    │   Database      │
                    └─────────────────┘
```

## 🔧 Configuration

### Database Schema

- **Patients**: Email, date of birth, condition, medical history
- **Conversation Sessions**: Session tracking and management
- **Conversation Interactions**: Message history with agent types
- **PRO Responses**: Structured patient outcome data
- **Trend Alerts**: Clinical alerts and recommendations

### Agent Configuration

Each agent can be configured for:

- **Language preferences** (multilingual support)
- **Accessibility needs** (visual, hearing, motor impairments)
- **Condition-specific templates** (diabetes, hypertension, depression, etc.)
- **Risk thresholds** (customizable alert levels)

## 🧪 Testing

### Run Simple Test

```bash
python simple_test.py
```

### Run Full API Test

```bash
python test_workflow.py
```

### Manual Testing

1. Start the server: `uvicorn main:app --reload`
2. Visit: `http://localhost:8000/docs` for Swagger UI
3. Test endpoints interactively

## 🔒 Security & Privacy

- **Authentication**: Email + date of birth (simplified for demo)
- **Data Storage**: Local SQLite with encryption capabilities
- **Compliance**: HIPAA-ready data handling patterns
- **Privacy**: De-identified data processing

## 📊 Key Features

### Patient Experience

- ✅ Conversational, natural language interactions
- ✅ Emotional intelligence and empathy
- ✅ Adaptive complexity based on comprehension
- ✅ Multilingual and accessibility support
- ✅ Real-time feedback and engagement

### Clinical Insights

- ✅ Trend analysis and pattern recognition
- ✅ Risk assessment and alert generation
- ✅ Evidence-based recommendations
- ✅ Predictive analytics for early intervention
- ✅ Comprehensive reporting and summaries

### Technical Excellence

- ✅ Scalable multi-agent architecture
- ✅ Stateful, persistent conversation tracking
- ✅ Real-time data processing and analysis
- ✅ Robust error handling and logging
- ✅ Comprehensive API documentation

## 🚀 Future Enhancements

- **React TypeScript Frontend**: Modern web interface
- **Mobile App**: Native iOS/Android applications
- **Integration APIs**: EHR system connectivity
- **Advanced Analytics**: Machine learning insights
- **Telemedicine Integration**: Video consultation support
- **Wearable Device Integration**: Real-time health data

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or support, please contact the development team or create an issue in the repository.
