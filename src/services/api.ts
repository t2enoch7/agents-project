import {
  User,
  Patient,
  HealthMetrics,
  ChatMessage,
  Conversation,
  Agent,
  DashboardMetrics,
  Alert,
  ApiResponse,
  LoginForm,
  HealthForm
} from '../types';

// Mock data storage
let currentUser: User | null = null;
let currentPatient: Patient | null = null;
let conversations: Conversation[] = [];
let alerts: Alert[] = [];

// Mock data
const mockUsers: User[] = [
  {
    id: '1',
    name: 'John Doe',
    dateOfBirth: '1990-05-15',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
  }
];

const mockPatients: Patient[] = [
  {
    id: '1',
    name: 'John Doe',
    dateOfBirth: '1990-05-15',
    age: 33,
    gender: 'male',
    location: 'New York, NY',
    height: '6\'0"',
    weight: '180 lbs',
    bmi: 24.4,
    bloodType: 'A+',
    activityLevel: 'moderate',
    dietaryPreferences: 'No restrictions',
    sleepHours: '7-8 hours',
    stressLevel: 'low',
    allergies: [],
    chronicConditions: ['Hypertension'],
    medications: []
  }
];

// Mock patient data
const mockPatient: Patient = {
  id: '1',
  name: 'Sophia Carter',
  dateOfBirth: '1993-05-15',
  age: 30,
  gender: 'female',
  location: 'San Francisco, CA',
  height: '5\'6"',
  weight: '135 lbs',
  bmi: 22.5,
  bloodType: 'O+',
  activityLevel: 'moderate',
  dietaryPreferences: 'Vegetarian',
  sleepHours: '7-8 hours',
  stressLevel: 'low',
  allergies: [],
  chronicConditions: [],
  medications: []
};

// Mock health metrics
const mockHealthMetrics: HealthMetrics = {
  heartRate: 72,
  bloodPressure: { systolic: 120, diastolic: 80 },
  sleep: 7.5,
  steps: 8500,
  weight: 135,
  bmi: 22.5,
  temperature: 98.6,
  oxygenSaturation: 98
};

// Mock dashboard metrics
const mockDashboardMetrics: DashboardMetrics = {
  completionRate: 95,
  alertAccuracy: 98,
  userSatisfaction: 92,
  activePatients: 1250,
  totalConversations: 3420,
  averageResponseTime: 2.3
};

// Mock agents
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Companion Agent',
    type: 'companion',
    status: 'active',
    capabilities: ['conversation', 'emotional_support', 'multilingual'],
    currentTask: 'Engaging with patient Sarah'
  },
  {
    id: '2',
    name: 'Questionnaire Agent',
    type: 'questionnaire',
    status: 'active',
    capabilities: ['adaptive_questions', 'personalization', 'comprehension_check'],
    currentTask: 'Adapting questions based on fatigue symptoms'
  },
  {
    id: '3',
    name: 'Monitoring Agent',
    type: 'monitoring',
    status: 'active',
    capabilities: ['trend_analysis', 'alert_generation', 'pattern_detection'],
    currentTask: 'Monitoring fatigue patterns'
  }
];

// Mock conversation
const mockConversation: Conversation = {
  id: '1',
  patientId: '1',
  messages: [
    {
      id: '1',
      sender: 'ai',
      content: 'Hello, how can I assist you today?',
      timestamp: new Date(Date.now() - 300000),
      type: 'text'
    },
    {
      id: '2',
      sender: 'user',
      content: 'I\'ve been experiencing some fatigue lately and wanted to discuss it.',
      timestamp: new Date(Date.now() - 240000),
      type: 'text'
    },
    {
      id: '3',
      sender: 'ai',
      content: 'I understand. Let\'s start by gathering some information. Can you describe the nature of your fatigue? Is it constant, or does it come and go?',
      timestamp: new Date(Date.now() - 180000),
      type: 'text'
    },
    {
      id: '4',
      sender: 'user',
      content: 'It\'s been pretty constant for the past few weeks, especially in the afternoons.',
      timestamp: new Date(Date.now() - 120000),
      type: 'text'
    },
    {
      id: '5',
      sender: 'ai',
      content: 'Okay. Have you noticed any other symptoms, such as changes in your sleep, appetite, or mood?',
      timestamp: new Date(Date.now() - 60000),
      type: 'text'
    }
  ],
  summary: 'Sarah has been experiencing constant fatigue for the past few weeks, particularly in the afternoons. No other symptoms reported yet.',
  status: 'active',
  createdAt: new Date(Date.now() - 300000),
  updatedAt: new Date(Date.now() - 60000)
};

// API Service Class
class ApiService {
  private baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

  // Authentication
  async login(credentials: LoginForm): Promise<ApiResponse<User>> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock validation
    if (!credentials.name || !credentials.dateOfBirth) {
      return {
        success: false,
        error: 'Name and date of birth are required'
      };
    }

    // Calculate age from date of birth
    const birthDate = new Date(credentials.dateOfBirth);
    const age = Math.floor((Date.now() - birthDate.getTime()) / (365.25 * 24 * 60 * 60 * 1000));

    const user: User = {
      id: '1',
      name: credentials.name,
      dateOfBirth: credentials.dateOfBirth,
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCkrmbCLea9oQATBsDwX15rlQDA6AzaF1N0u-n9oqgStMt74PYek3tBQHd85TUXsB2U5RV6P7Cn7GIlRgwo4UNhkGE-HO_ThwagyDgoDWPr5zGkDDCICl4Lu8UwitfOi4Pl9RiTYaijDBMR-kvcPOqqpP_L8ol1tSb2Y4O13IyTCknPi6BUf_csBGtyRNegXtwIr_C0JwzZGVpnNecfMb3u4GNTfhhqbX3pi0MvO9vJZ4Nm5mZ63Wwcq_RtbJbzPhdZ_IH06umKcRoH'
    };

    currentUser = user;
    currentPatient = { ...mockPatient, ...user, age };

    return {
      success: true,
      data: user,
      message: 'Login successful'
    };
  }

  async logout(): Promise<ApiResponse<void>> {
    await new Promise(resolve => setTimeout(resolve, 500));
    currentUser = null;
    currentPatient = null;
    return { success: true };
  }

  // Patient Data
  async getCurrentPatient(): Promise<ApiResponse<Patient>> {
    await new Promise(resolve => setTimeout(resolve, 500));

    if (!currentPatient) {
      return {
        success: false,
        error: 'No patient data available'
      };
    }

    return {
      success: true,
      data: currentPatient
    };
  }

  async updatePatientHealthData(healthData: HealthForm): Promise<ApiResponse<Patient>> {
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (!currentPatient) {
      return {
        success: false,
        error: 'No patient data available'
      };
    }

    // Update patient data
    currentPatient = {
      ...currentPatient,
      ...healthData
    };

    return {
      success: true,
      data: currentPatient,
      message: 'Health data updated successfully'
    };
  }

  // Health Metrics
  async getHealthMetrics(): Promise<ApiResponse<HealthMetrics>> {
    await new Promise(resolve => setTimeout(resolve, 800));

    return {
      success: true,
      data: mockHealthMetrics
    };
  }

  // Dashboard
  async getDashboardMetrics(): Promise<ApiResponse<DashboardMetrics>> {
    await new Promise(resolve => setTimeout(resolve, 600));

    return {
      success: true,
      data: mockDashboardMetrics
    };
  }

  // Chat and Conversations
  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    await new Promise(resolve => setTimeout(resolve, 500));

    if (conversations.length === 0) {
      conversations = [mockConversation];
    }

    return {
      success: true,
      data: conversations
    };
  }

  async getConversation(id: string): Promise<ApiResponse<Conversation>> {
    await new Promise(resolve => setTimeout(resolve, 300));

    const conversation = conversations.find(c => c.id === id) || mockConversation;

    return {
      success: true,
      data: conversation
    };
  }

  async sendMessage(conversationId: string, content: string): Promise<ApiResponse<ChatMessage>> {
    await new Promise(resolve => setTimeout(resolve, 1000));

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content,
      timestamp: new Date(),
      type: 'text'
    };

    // Add message to conversation
    const conversation = conversations.find(c => c.id === conversationId) || mockConversation;
    conversation.messages.push(newMessage);
    conversation.updatedAt = new Date();

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: this.generateAIResponse(content),
        timestamp: new Date(),
        type: 'text'
      };
      conversation.messages.push(aiResponse);
      conversation.updatedAt = new Date();
    }, 2000);

    return {
      success: true,
      data: newMessage
    };
  }

  // Agents
  async getAgents(): Promise<ApiResponse<Agent[]>> {
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      data: mockAgents
    };
  }

  // Alerts
  async getAlerts(): Promise<ApiResponse<Alert[]>> {
    await new Promise(resolve => setTimeout(resolve, 400));

    if (alerts.length === 0) {
      alerts = [
        {
          id: '1',
          patientId: '1',
          type: 'health',
          severity: 'medium',
          message: 'Fatigue pattern detected - consider lifestyle adjustments',
          timestamp: new Date(Date.now() - 3600000),
          status: 'active'
        }
      ];
    }

    return {
      success: true,
      data: alerts
    };
  }

  // Helper method to generate AI responses
  private generateAIResponse(userMessage: string): string {
    const responses = [
      'I understand your concern. Let me help you explore this further.',
      'That\'s important information. Can you tell me more about when this started?',
      'Thank you for sharing that. How does this affect your daily activities?',
      'I see. Have you noticed any patterns or triggers?',
      'That sounds challenging. What have you tried so far to manage this?',
      'I appreciate you bringing this up. Let\'s work together to find solutions.',
      'This is valuable information. How would you rate the severity on a scale of 1-10?',
      'I\'m here to support you. What would be most helpful for you right now?'
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }
}

export const apiService = new ApiService();
export default apiService;
