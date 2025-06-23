import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import WelcomePage from "./pages/WelcomePage";
import PatientChatPage from "./pages/PatientChatPage";
import SummaryPage from "./pages/SummaryPage";
import DashboardPage from "./pages/DashboardPage";
import { useAuth } from "./context/AuthContext";

function ProtectedRoute({
  children,
  role,
}: {
  children: React.ReactNode;
  role: "patient" | "clinician";
}) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route
          path="/chat"
          element={
            <ProtectedRoute role="patient">
              <PatientChatPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/summary"
          element={
            <ProtectedRoute role="patient">
              <SummaryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute role="clinician">
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
