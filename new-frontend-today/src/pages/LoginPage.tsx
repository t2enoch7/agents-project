import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Stack,
} from "@mui/material";
import {
  HealthAndSafety,
  Psychology,
  TrendingUp,
  Security,
} from "@mui/icons-material";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, dateOfBirth);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: <HealthAndSafety sx={{ fontSize: 40, color: "primary.main" }} />,
      title: "Companion Agent",
      description:
        "Personalized healthcare conversations with AI-powered support",
    },
    {
      icon: <Psychology sx={{ fontSize: 40, color: "secondary.main" }} />,
      title: "Adaptive Questionnaires",
      description: "Intelligent PRO data collection tailored to your needs",
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40, color: "success.main" }} />,
      title: "Trend Monitoring",
      description: "Advanced analytics to track your health patterns",
    },
    {
      icon: <Security sx={{ fontSize: 40, color: "info.main" }} />,
      title: "Privacy First",
      description:
        "Your health data is protected with enterprise-grade security",
    },
  ];

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #1976d2 0%, #388e3c 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
      }}
    >
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={4}
        maxWidth="1200px"
        alignItems="center"
      >
        {/* Features Section */}
        <Stack
          sx={{
            color: "white",
            textAlign: "center",
            width: { xs: "100%", md: "50%" },
          }}
          spacing={3}
        >
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <HealthAndSafety sx={{ fontSize: 60, mr: 2 }} />
            <Typography variant="h3" component="h1" fontWeight="bold">
              PRO Health
            </Typography>
          </Box>
          <Typography variant="h5" sx={{ opacity: 0.9 }}>
            Multi-Agent Patient Reported Outcomes System
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.8 }}>
            Experience the future of healthcare with AI-powered agents designed
            to support your health journey
          </Typography>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: 2,
              mt: 2,
            }}
          >
            {features.map((feature, index) => (
              <Paper
                key={index}
                sx={{
                  p: 2,
                  textAlign: "center",
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                  backdropFilter: "blur(10px)",
                  border: "1px solid rgba(255, 255, 255, 0.2)",
                  color: "white",
                  height: "100%",
                }}
              >
                <Box sx={{ mb: 1 }}>{feature.icon}</Box>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                  {feature.title}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  {feature.description}
                </Typography>
              </Paper>
            ))}
          </Box>
        </Stack>

        {/* Login Form */}
        <Box sx={{ width: { xs: "100%", md: "50%" } }}>
          <Card
            sx={{
              maxWidth: 400,
              mx: "auto",
              borderRadius: 3,
              boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
            }}
          >
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: "center", mb: 3 }}>
                <HealthAndSafety
                  sx={{ fontSize: 48, color: "primary.main", mb: 2 }}
                />
                <Typography variant="h4" component="h2" gutterBottom>
                  Welcome Back
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Sign in to access your personalized health dashboard
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  sx={{ mb: 3 }}
                  variant="outlined"
                />

                <TextField
                  fullWidth
                  label="Date of Birth"
                  type="date"
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                  required
                  sx={{ mb: 3 }}
                  variant="outlined"
                  InputLabelProps={{
                    shrink: true,
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{
                    py: 1.5,
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    borderRadius: 2,
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    "Sign In"
                  )}
                </Button>
              </Box>

              <Box sx={{ mt: 3, textAlign: "center" }}>
                <Typography variant="body2" color="text.secondary">
                  Secure authentication using your email and date of birth
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Stack>
    </Box>
  );
};

export default LoginPage;
