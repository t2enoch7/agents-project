// User and Patient Types
export interface User {
  id: string;
  name: string;
  dateOfBirth: string;
  email?: string;
  avatar?: string;
}

export interface Patient extends User {
  age: number;
  gender: 'male' | 'female' | 'other';
  location: string;
  height: string;
  weight: string;
  bmi: number;
  bloodType: string;
  activityLevel: 'low' | 'moderate' | 'high';
  dietaryPreferences: string;
  sleepHours: string;
  stressLevel: 'low' | 'moderate' | 'high';
  allergies: string[];
  chronicConditions: string[];
  medications: string[];
}

// Health Metrics Types
export interface HealthMetrics {
  heartRate: number;
  bloodPressure: {
    systolic: number;
    diastolic: number;
  };
  sleep: number;
  steps: number;
  weight: number;
  bmi: number;
  temperature: number;
  oxygenSaturation: number;
}

// Chat and Conversation Types
export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  timestamp: Date;
  type: 'text' | 'image' | 'file';
  metadata?: {
    emotion?: string;
    confidence?: number;
    suggestedActions?: string[];
  };
}

export interface Conversation {
  id: string;
  patientId: string;
  messages: ChatMessage[];
  summary: string;
  status: 'active' | 'completed' | 'archived';
  createdAt: Date;
  updatedAt: Date;
}

// Agent Types for Multi-Agent System
export interface Agent {
  id: string;
  name: string;
  type: 'companion' | 'questionnaire' | 'monitoring';
  status: 'active' | 'inactive' | 'error';
  capabilities: string[];
  currentTask?: string;
}

export interface CompanionAgent extends Agent {
  type: 'companion';
  personality: string;
  language: string;
  accessibilityFeatures: string[];
}

export interface QuestionnaireAgent extends Agent {
  type: 'questionnaire';
  currentQuestionnaire?: string;
  adaptationLevel: 'low' | 'medium' | 'high';
  questionHistory: string[];
}

export interface MonitoringAgent extends Agent {
  type: 'monitoring';
  monitoringMetrics: string[];
  alertThresholds: Record<string, number>;
  trendAnalysis: TrendData[];
}

// Dashboard and Analytics Types
export interface DashboardMetrics {
  completionRate: number;
  alertAccuracy: number;
  userSatisfaction: number;
  activePatients: number;
  totalConversations: number;
  averageResponseTime: number;
}

export interface TrendData {
  metric: string;
  value: number;
  timestamp: Date;
  trend: 'increasing' | 'decreasing' | 'stable';
  change: number;
}

export interface Alert {
  id: string;
  patientId: string;
  type: 'health' | 'engagement' | 'system';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: Date;
  status: 'active' | 'acknowledged' | 'resolved';
  metadata?: Record<string, any>;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Form Types
export interface LoginForm {
  name: string;
  dateOfBirth: string;
}

export interface HealthForm {
  height: string;
  weight: string;
  bloodType: string;
  activityLevel: 'low' | 'moderate' | 'high';
  dietaryPreferences: string;
  sleepHours: string;
  stressLevel: 'low' | 'moderate' | 'high';
  allergies: string[];
  chronicConditions: string[];
  medications: string[];
}

// Navigation Types
export type Route = '/' | '/dashboard' | '/chat' | '/summary' | '/profile';

export interface NavigationItem {
  path: Route;
  label: string;
  icon: string;
  requiresAuth: boolean;
}
