import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userDateOfBirth');
      localStorage.removeItem('userId');
      localStorage.removeItem('userCondition');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  login: (email: string, dateOfBirth: string) =>
    api.post('/auth/login', { email, date_of_birth: dateOfBirth }),

  register: (email: string, dateOfBirth: string, name: string) =>
    api.post('/auth/register', { email, date_of_birth: dateOfBirth, name }),
};

export const patientAPI = {
  getProfile: () => api.get('/patients/profile'),
  updateProfile: (data: any) => api.put('/patients/profile', data),
  getHistory: () => api.get('/patients/history'),
};

export const conversationAPI = {
  start: () => api.post('/conversations/start'),
  continue: (message: string, sessionId: string) =>
    api.post('/conversations/continue', { message, session_id: sessionId }),
  analyze: () => api.post('/conversations/analyze'),
  complete: (sessionId: string) =>
    api.post('/conversations/complete', { session_id: sessionId }),
};

export const clinicianAPI = {
  getPatients: () => api.get('/clinicians/patients'),
  getPatientDetails: (patientId: string) => api.get(`/clinicians/patients/${patientId}`),
  getAlerts: () => api.get('/clinicians/alerts'),
  sendAlert: (patientId: string, message: string) =>
    api.post('/clinicians/alerts', { patient_id: patientId, message }),
  getInsights: () => api.get('/clinicians/insights'),
};

// Add mock clinician methods for the frontend-only dashboard
const mockApi = {
  async getFlaggedPatients() {
    await new Promise((res) => setTimeout(res, 500));
    return {
      data: [
        {
          name: "Jane Doe",
          email: "jane@example.com",
          lastCheckIn: "2024-06-25",
          riskScore: 0.85,
          issue: "Blood pressure trending upward"
        },
        {
          name: "John Smith",
          email: "john@example.com",
          lastCheckIn: "2024-06-24",
          riskScore: 0.75,
          issue: "Mood instability detected"
        }
      ]
    };
  },
  async searchPatient(query: string) {
    await new Promise((res) => setTimeout(res, 500));
    if (query.toLowerCase().includes("jane")) {
      return {
        data: {
          name: "Jane Doe",
          email: "jane@example.com",
          lastCheckIn: "2024-06-25",
          riskScore: 0.85,
          issue: "Blood pressure trending upward"
        }
      };
    }
    if (query.toLowerCase().includes("john")) {
      return {
        data: {
          name: "John Smith",
          email: "john@example.com",
          lastCheckIn: "2024-06-24",
          riskScore: 0.75,
          issue: "Mood instability detected"
        }
      };
    }
    throw new Error("Patient not found");
  },
  async notifyPatient(email: string, message: string) {
    await new Promise((res) => setTimeout(res, 500));
    return { data: { success: true } };
  },
  async searchPatientByEmailAndDob(email: string, dob: string) {
    await new Promise((res) => setTimeout(res, 500));
    if (email === "jane@example.com" && dob === "1990-01-01") {
      return {
        data: {
          name: "Jane Doe",
          email,
          dob,
          trends: [
            { date: "2024-06-01", value: 0.7, label: "Fatigue" },
            { date: "2024-06-10", value: 0.9, label: "Pain" },
          ],
          alerts: ["High pain score on 2024-06-10"],
          questionnaireHistory: [
            { date: "2024-06-01", answers: { q1: "Yes", q2: "No" } },
            { date: "2024-06-10", answers: { q1: "No", q2: "Yes" } },
          ],
        },
      };
    }
    throw new Error("Patient not found");
  },
};

// Merge mockApi into the default export
export default Object.assign(api, mockApi);
