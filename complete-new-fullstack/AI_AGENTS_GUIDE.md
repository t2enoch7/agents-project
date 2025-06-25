# AI Agents Integration Guide

This guide explains how to use the multi-agent AI system from the frontend for Patient Reported Outcomes (PROs).

## 🏗️ System Architecture

The system consists of three coordinated AI agents:

### 1. **Companion Agent** 🤖

- **Purpose**: Initiates check-ins and maintains conversational flow
- **Responsibilities**:
  - Welcomes patients and explains the process
  - Manages conversation state and transitions
  - Provides emotional support and encouragement
  - Generates completion messages and summaries

### 2. **Adaptive Questionnaire Agent** 📝

- **Purpose**: Personalizes question delivery based on patient responses
- **Responsibilities**:
  - Adapts question complexity and tone
  - Detects emotional cues in responses
  - Adjusts questioning strategy based on patient engagement
  - Supports multilingual and accessibility standards

### 3. **Trend Monitoring Agent** 📊

- **Purpose**: Detects patterns and triggers clinical insights
- **Responsibilities**:
  - Analyzes response patterns over time
  - Identifies risk signals and concerning trends
  - Generates clinical insights and recommendations
  - Flags alerts for healthcare providers

## 🚀 Frontend Integration

### Starting a Conversation

1. **Navigate to AI Conversation**: Click "AI Conversation" in the navigation or "Start AI Conversation" from the dashboard
2. **Initiate Session**: Click "Start Conversation" to begin
3. **Agent Response**: The Companion Agent will welcome you and ask how you're feeling

```typescript
// Frontend API call
const response = await conversationAPI.start();
const { session_id, response: agentResponse, agent_type } = response.data;
```

### Continuing the Conversation

1. **Type Your Message**: Enter your response in the chat interface
2. **Send Message**: Click send or press Enter
3. **Agent Processing**: The appropriate agent will respond based on context

```typescript
// Frontend API call
const response = await conversationAPI.continue(message, sessionId);
const { response: agentResponse, agent_type, emotional_state } = response.data;
```

### Analyzing Trends

1. **Automatic Analysis**: After several exchanges, the system automatically analyzes trends
2. **Manual Analysis**: Click "Analyze Trends" button to trigger analysis
3. **View Results**: See risk scores, patterns, and recommendations

```typescript
// Frontend API call
const response = await conversationAPI.analyze();
const { analysis } = response.data;
```

### Completing the Session

1. **Generate Summary**: Click "Complete Session" to finish
2. **Review Summary**: View questionnaire summary with key findings
3. **Get Recommendations**: Receive personalized health recommendations

```typescript
// Frontend API call
const response = await conversationAPI.complete(sessionId);
const { completion_message, session_summary } = response.data;
```

## 🎯 Conversation Flow

### Typical Session Structure

1. **Welcome Phase** (Companion Agent)

   - Greeting and explanation
   - Initial mood assessment

2. **Questioning Phase** (Adaptive Questionnaire Agent)

   - Personalized health questions
   - Emotional state monitoring
   - Adaptive complexity adjustment

3. **Analysis Phase** (Trend Monitoring Agent)

   - Pattern recognition
   - Risk assessment
   - Clinical insight generation

4. **Completion Phase** (Companion Agent)
   - Summary generation
   - Thank you message
   - Next steps recommendation

### Agent Transitions

The system automatically transitions between agents based on:

- **Conversation length**: Longer conversations trigger trend analysis
- **Response patterns**: Emotional cues influence agent selection
- **Question complexity**: Adaptive questionnaire adjusts difficulty
- **Risk signals**: Concerning responses trigger trend monitoring

## 📊 Data Collection & Analysis

### What Data is Collected

- **Patient Responses**: All conversation messages
- **Emotional States**: Mood and confidence levels
- **Response Patterns**: Timing and engagement metrics
- **Health Indicators**: Self-reported symptoms and concerns

### Analysis Features

- **Risk Scoring**: 0-1 scale based on response patterns
- **Trend Detection**: Longitudinal pattern analysis
- **Recommendation Generation**: Personalized health advice
- **Alert System**: Automatic flagging of concerning patterns

## 🔧 Technical Implementation

### Backend API Endpoints

```python
# Start conversation
POST /conversations/start
Response: { session_id, response, agent_type, emotional_state }

# Continue conversation
POST /conversations/continue
Body: { message, session_id }
Response: { response, agent_type, emotional_state }

# Analyze trends
POST /conversations/analyze
Response: { analysis }

# Complete session
POST /conversations/complete
Body: { session_id }
Response: { completion_message, session_summary }
```

### Frontend Components

- **ConversationPage**: Main chat interface
- **Message Components**: Display user and agent messages
- **Agent Icons**: Visual indicators for different agent types
- **Summary Dialog**: Questionnaire results and recommendations

### State Management

- **Session State**: Tracks conversation progress
- **Message History**: Stores all conversation messages
- **Agent Context**: Maintains current agent and emotional state
- **Analysis Results**: Stores trend analysis and recommendations

## 🎨 User Experience Features

### Visual Indicators

- **Agent Icons**: Different icons for each agent type
- **Emotional States**: Color-coded mood indicators
- **Progress Tracking**: Stepper showing conversation phases
- **Risk Visualization**: Progress bars for risk scores

### Accessibility Features

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and descriptions
- **High Contrast**: Accessible color schemes
- **Multilingual Support**: Internationalization ready

### Responsive Design

- **Mobile Optimized**: Touch-friendly interface
- **Desktop Enhanced**: Full-featured desktop experience
- **Tablet Support**: Optimized for tablet devices

## 🧪 Testing the System

### Mock Server

For development and testing, use the mock backend server:

```bash
# Start mock server
python mock_backend_server.py

# Test endpoints
curl -X POST http://localhost:8001/conversations/start
curl -X POST http://localhost:8001/conversations/continue \
  -H "Content-Type: application/json" \
  -d '{"message": "I feel good today", "session_id": "session_123"}'
```

### Frontend Testing

1. **Start Frontend**: `cd frontend && npm start`
2. **Login**: Use any email/date combination
3. **Navigate**: Go to AI Conversation page
4. **Test Flow**: Complete a full conversation session

### Expected Behavior

- **Agent Transitions**: Smooth transitions between agents
- **Response Adaptation**: Questions adapt to your responses
- **Emotional Detection**: System responds to emotional cues
- **Summary Generation**: Comprehensive session summary
- **Recommendations**: Personalized health advice

## 🔒 Privacy & Security

### Data Protection

- **Local Storage**: Session data stored locally
- **No Persistence**: Mock server doesn't persist data
- **Token-based Auth**: Simple authentication system
- **CORS Enabled**: Cross-origin requests supported

### Production Considerations

- **HTTPS**: Secure communication required
- **Database**: Persistent storage for patient data
- **Encryption**: End-to-end encryption for sensitive data
- **Compliance**: HIPAA and GDPR compliance

## 🚀 Next Steps

### Production Deployment

1. **Backend Setup**: Deploy FastAPI with real database
2. **Google AI Integration**: Add Google AI SDK for Gemini 2.0 Pro
3. **Authentication**: Implement proper JWT authentication
4. **Monitoring**: Add logging and analytics

### Feature Enhancements

1. **Clinician Dashboard**: Healthcare provider interface
2. **Alert System**: Real-time notifications
3. **Integration**: EHR system integration
4. **Analytics**: Advanced reporting and insights

### Scaling Considerations

1. **Load Balancing**: Multiple server instances
2. **Caching**: Redis for session management
3. **Queue System**: Background task processing
4. **Microservices**: Agent separation for scalability

## 📚 Additional Resources

- **API Documentation**: See `main.py` for full endpoint details
- **Agent Implementation**: Check `utils/` directory for agent code
- **Frontend Components**: Review `frontend/src/pages/ConversationPage.tsx`
- **Testing Examples**: Run `test_conversation_frontend.py` for examples

---

This AI agents system provides a comprehensive, patient-centered approach to health monitoring and support, leveraging the power of multiple specialized AI agents working in coordination.



User Type	Email Example	Date of Birth	Result (Current)
Patient	patient@pro.com	1990-01-01	Patient dashboard/flow
Clinician	clinician@pro.com	1980-05-05	Patient dashboard/flow (no difference)
