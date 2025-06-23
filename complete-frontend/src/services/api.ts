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
