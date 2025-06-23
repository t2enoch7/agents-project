import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  ReactNode,
} from "react";
import { User, Patient, LoginForm } from "../types";
import { login, getCurrentPatient, logout } from "../services/api";

interface AuthState {
  user: User | null;
  patient: Patient | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: "LOGIN_START" }
  | { type: "LOGIN_SUCCESS"; payload: { user: User; patient: Patient } }
  | { type: "LOGIN_FAILURE"; payload: string }
  | { type: "LOGOUT" }
  | { type: "UPDATE_PATIENT"; payload: Patient }
  | { type: "CLEAR_ERROR" };

const initialState: AuthState = {
  user: null,
  patient: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case "LOGIN_START":
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case "LOGIN_SUCCESS":
      return {
        ...state,
        user: action.payload.user,
        patient: action.payload.patient,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case "LOGIN_FAILURE":
      return {
        ...state,
        isLoading: false,
        error: action.payload,
      };
    case "LOGOUT":
      return {
        ...initialState,
      };
    case "UPDATE_PATIENT":
      return {
        ...state,
        patient: action.payload,
      };
    case "CLEAR_ERROR":
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
};

interface AuthContextType extends AuthState {
  login: (credentials: LoginForm) => Promise<void>;
  logout: () => Promise<void>;
  updatePatient: (patient: Patient) => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const login = async (credentials: LoginForm) => {
    dispatch({ type: "LOGIN_START" });

    try {
      const response = await login(credentials);

      if (response.success && response.data) {
        const patientResponse = await getCurrentPatient();

        if (patientResponse.success && patientResponse.data) {
          dispatch({
            type: "LOGIN_SUCCESS",
            payload: { user: response.data, patient: patientResponse.data },
          });
        } else {
          dispatch({
            type: "LOGIN_FAILURE",
            payload: "Failed to load patient data",
          });
        }
      } else {
        dispatch({
          type: "LOGIN_FAILURE",
          payload: response.error || "Login failed",
        });
      }
    } catch (error) {
      dispatch({
        type: "LOGIN_FAILURE",
        payload: "An unexpected error occurred",
      });
    }
  };

  const logout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      dispatch({ type: "LOGOUT" });
    }
  };

  const updatePatient = (patient: Patient) => {
    dispatch({ type: "UPDATE_PATIENT", payload: patient });
  };

  const clearError = () => {
    dispatch({ type: "CLEAR_ERROR" });
  };

  // Check for existing session on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const patientResponse = await getCurrentPatient();
        if (patientResponse.success && patientResponse.data) {
          // If we have patient data, assume user is logged in
          const user: User = {
            id: patientResponse.data.id,
            name: patientResponse.data.name,
            dateOfBirth: patientResponse.data.dateOfBirth,
            avatar: patientResponse.data.avatar,
          };
          dispatch({
            type: "LOGIN_SUCCESS",
            payload: { user, patient: patientResponse.data },
          });
        }
      } catch (error) {
        console.error("Auth check error:", error);
      }
    };

    checkAuth();
  }, []);

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    updatePatient,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
