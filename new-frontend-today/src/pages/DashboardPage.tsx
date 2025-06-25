import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  CircularProgress,
  Stack,
} from "@mui/material";
import {
  HealthAndSafety,
  TrendingUp,
  Chat,
  CheckCircle,
  Warning,
  Person,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

interface HealthMetrics {
  riskScore: number;
  lastCheckIn: string;
  totalSessions: number;
  flagged: boolean;
  alerts: string[];
  trends: Array<{ date: string; label: string; value: number }>;
}

interface RecentActivity {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  status: string;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(
    null
  );
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      // Mock data for now - in real app, fetch from API
      setHealthMetrics({
        riskScore: 0.3,
        lastCheckIn: "2024-01-15",
        totalSessions: 12,
        flagged: false,
        alerts: ["No concerning trends detected."],
        trends: [
          { date: "2024-06-01", label: "Fatigue", value: 0.2 },
          { date: "2024-06-10", label: "Pain", value: 0.3 },
        ],
      });
      setRecentActivity([
        {
          id: "1",
          type: "conversation",
          message: "Completed daily health check-in",
          timestamp: "2024-01-15 09:30",
          status: "completed",
        },
        {
          id: "2",
          type: "alert",
          message: "Blood sugar levels trending upward",
          timestamp: "2024-01-14 14:20",
          status: "active",
        },
        {
          id: "3",
          type: "questionnaire",
          message: "Submitted PRO questionnaire",
          timestamp: "2024-01-13 16:45",
          status: "completed",
        },
      ]);
      setError("");
    } catch (err) {
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const getRiskColor = (score: number) => {
    if (score < 0.3) return "success";
    if (score < 0.7) return "warning";
    return "error";
  };

  const getRiskLabel = (score: number) => {
    if (score < 0.3) return "Low Risk";
    if (score < 0.7) return "Medium Risk";
    return "High Risk";
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        maxWidth: 700,
        mx: "auto",
        mt: 4,
        bgcolor: "#fff",
        borderRadius: 2,
        boxShadow: 2,
        p: 4,
        color: "#111",
      }}
      aria-label="Patient Dashboard"
    >
      <Typography
        variant="h3"
        gutterBottom
        sx={{
          color: "#111",
          fontWeight: 700,
          fontSize: "2.2rem",
          letterSpacing: 0.5,
        }}
      >
        Welcome, {user?.email}
      </Typography>
      <Divider sx={{ my: 2, bgcolor: "#222" }} />
      {error && (
        <Alert
          severity="error"
          sx={{
            bgcolor: "#fff0f0",
            color: "#b00020",
            fontWeight: 600,
            border: "1px solid #b00020",
            mt: 2,
          }}
          role="alert"
        >
          {error}
        </Alert>
      )}
      {loading ? (
        <Typography sx={{ color: "#111", fontSize: "1.2rem" }}>
          Loading...
        </Typography>
      ) : (
        healthMetrics && (
          <Box>
            <Typography
              variant="h5"
              sx={{ color: "#111", fontWeight: 700, mt: 3, mb: 1 }}
            >
              Your Health Overview
            </Typography>
            <Typography sx={{ color: "#222", fontSize: "1.1rem" }}>
              Last Check-in: {healthMetrics.lastCheckIn}
            </Typography>
            <Typography sx={{ color: "#222", fontSize: "1.1rem" }}>
              Total Sessions: {healthMetrics.totalSessions}
            </Typography>
            <Typography
              sx={{
                color: healthMetrics.riskScore > 0.7 ? "#b00020" : "#111",
                fontWeight: 700,
                fontSize: "1.1rem",
              }}
            >
              Risk Score: {healthMetrics.riskScore}
            </Typography>
            <Divider sx={{ my: 2, bgcolor: "#222" }} />
            <Typography
              variant="subtitle1"
              sx={{ color: "#111", fontWeight: 600 }}
            >
              Trends:
            </Typography>
            <List>
              {healthMetrics.trends.map((trend, idx) => (
                <ListItem
                  key={idx}
                  sx={{
                    color: trend.value > 0.7 ? "#b00020" : "#111",
                    fontWeight: trend.value > 0.7 ? 700 : 500,
                  }}
                  aria-label={`Trend ${trend.label} on ${trend.date}`}
                >
                  {trend.date}: {trend.label} - {trend.value}
                </ListItem>
              ))}
            </List>
            <Typography
              variant="subtitle1"
              sx={{ color: "#111", fontWeight: 600 }}
            >
              Alerts:
            </Typography>
            <List>
              {healthMetrics.alerts.map((alert, idx) => (
                <ListItem
                  key={idx}
                  sx={{
                    color: alert.includes("No concerning")
                      ? "#006400"
                      : "#b00020",
                    fontWeight: 700,
                  }}
                  aria-label={`Alert ${idx + 1}`}
                >
                  {alert}
                </ListItem>
              ))}
            </List>
            <Button
              variant="contained"
              sx={{
                mt: 3,
                bgcolor: "#111",
                color: "#fff",
                fontWeight: 700,
                "&:hover": { bgcolor: "#333" },
              }}
              onClick={() => navigate("/conversation")}
              aria-label="Start New Check-in"
            >
              Start New Check-in
            </Button>
          </Box>
        )
      )}
    </Box>
  );
};

export default DashboardPage;
