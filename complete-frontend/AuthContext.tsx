import React, { createContext, useContext, useState, ReactNode } from "react";

export type UserRole = "patient" | "clinician";
export interface AuthState {
  name: string;
  dob: string;
  role: UserRole;
}

interface AuthContextType {
  user: AuthState | null;
  login: (user: AuthState) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthState | null>(null);
  const login = (user: AuthState) => setUser(user);
  const logout = () => setUser(null);
  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
