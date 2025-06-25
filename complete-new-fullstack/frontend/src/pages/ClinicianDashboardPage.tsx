import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  List,
  ListItem,
  Divider,
} from "@mui/material";
import api from "../services/api";

const ClinicianDashboardPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [dob, setDob] = useState("");
  const [patient, setPatient] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [notifyMsg, setNotifyMsg] = useState("");
  const [notifyStatus, setNotifyStatus] = useState<string | null>(null);

  const handleSearch = async () => {
    setError("");
    setPatient(null);
    setNotifyMsg("");
    setNotifyStatus(null);
    setLoading(true);
    try {
      const res = await api.searchPatientByEmailAndDob(email, dob);
      setPatient(res.data);
    } catch (err: any) {
      setError("Patient not found or error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleNotify = async () => {
    setNotifyStatus(null);
    try {
      await api.notifyPatient(patient.email, notifyMsg);
      setNotifyStatus("Notification sent!");
      setNotifyMsg("");
    } catch (err) {
      setNotifyStatus("Failed to send notification");
    }
  };

  // Show notification UI if there are alerts or any trend value > 0.7
  const showNotify =
    patient &&
    ((patient.alerts && patient.alerts.length > 0) ||
      (patient.trends && patient.trends.some((t: any) => t.value > 0.7)));

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
      aria-label="Clinician Dashboard"
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
        Clinician Dashboard
      </Typography>
      <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap" }}>
        <TextField
          label="Patient Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          fullWidth
          inputProps={{
            "aria-label": "Patient Email",
            style: { background: "#fff", color: "#111" },
          }}
          InputLabelProps={{ style: { color: "#222" } }}
        />
        <TextField
          label="Date of Birth"
          type="date"
          value={dob}
          onChange={(e) => setDob(e.target.value)}
          InputLabelProps={{ shrink: true, style: { color: "#222" } }}
          fullWidth
          inputProps={{
            "aria-label": "Date of Birth",
            style: { background: "#fff", color: "#111" },
          }}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={loading}
          sx={{
            bgcolor: "#111",
            color: "#fff",
            fontWeight: 700,
            fontSize: "1.1rem",
            px: 3,
            py: 1.5,
            borderRadius: 1,
            "&:hover": { bgcolor: "#333" },
          }}
          aria-label="Search Patient"
        >
          {loading ? "Searching..." : "Search"}
        </Button>
      </Box>
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
      {patient && (
        <Box>
          <Typography
            variant="h5"
            sx={{ color: "#111", fontWeight: 700, mt: 3, mb: 1 }}
          >
            Patient: {patient.name}
          </Typography>
          <Typography sx={{ color: "#222", fontSize: "1.1rem" }}>
            Email: {patient.email}
          </Typography>
          <Typography sx={{ color: "#222", fontSize: "1.1rem" }}>
            DOB: {patient.dob}
          </Typography>
          <Divider sx={{ my: 2, bgcolor: "#222" }} />
          <Typography
            variant="subtitle1"
            sx={{ color: "#111", fontWeight: 600 }}
          >
            Trends:
          </Typography>
          <List>
            {patient.trends.map((trend: any, idx: number) => (
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
            {patient.alerts.map((alert: string, idx: number) => (
              <ListItem
                key={idx}
                sx={{ color: "#b00020", fontWeight: 700 }}
                aria-label={`Alert ${idx + 1}`}
              >
                {alert}
              </ListItem>
            ))}
          </List>
          <Typography
            variant="subtitle1"
            sx={{ color: "#111", fontWeight: 600 }}
          >
            Questionnaire History:
          </Typography>
          <List>
            {patient.questionnaireHistory.map((q: any, idx: number) => (
              <ListItem
                key={idx}
                sx={{ color: "#111", fontWeight: 500 }}
                aria-label={`Questionnaire on ${q.date}`}
              >
                {q.date}: {JSON.stringify(q.answers)}
              </ListItem>
            ))}
          </List>
          {showNotify && (
            <Box sx={{ mt: 3 }}>
              <Typography
                variant="subtitle1"
                sx={{ color: "#111", fontWeight: 600 }}
              >
                Send Notification to Patient:
              </Typography>
              <TextField
                label="Notification Message"
                value={notifyMsg}
                onChange={(e) => setNotifyMsg(e.target.value)}
                fullWidth
                multiline
                minRows={2}
                sx={{ mt: 1, bgcolor: "#fff" }}
                inputProps={{
                  "aria-label": "Notification Message",
                  style: { color: "#111" },
                }}
                InputLabelProps={{ style: { color: "#222" } }}
              />
              <Button
                variant="contained"
                sx={{
                  mt: 2,
                  bgcolor: "#111",
                  color: "#fff",
                  fontWeight: 700,
                  "&:hover": { bgcolor: "#333" },
                }}
                onClick={handleNotify}
                disabled={!notifyMsg}
                aria-label="Send Notification"
              >
                Send Notification
              </Button>
              {notifyStatus && (
                <Alert
                  severity={notifyStatus.includes("sent") ? "success" : "error"}
                  sx={{
                    mt: 2,
                    bgcolor: notifyStatus.includes("sent")
                      ? "#e6ffe6"
                      : "#fff0f0",
                    color: notifyStatus.includes("sent")
                      ? "#006400"
                      : "#b00020",
                    border: notifyStatus.includes("sent")
                      ? "1px solid #006400"
                      : "1px solid #b00020",
                    fontWeight: 600,
                  }}
                  role="alert"
                >
                  {notifyStatus}
                </Alert>
              )}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default ClinicianDashboardPage;
