import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  LinearProgress,
} from "@mui/material";
import {
  Send,
  Psychology,
  TrendingUp,
  CheckCircle,
  Person,
  SmartToy,
} from "@mui/icons-material";
import { useAuth } from "../contexts/AuthContext";
import { conversationAPI } from "../services/api";

interface Message {
  id: string;
  text: string;
  sender: "user" | "agent";
  agentType?: string;
  timestamp: Date;
  emotionalState?: any;
}

interface QuestionnaireSummary {
  totalQuestions: number;
  completedQuestions: number;
  keyFindings: string[];
  recommendations: string[];
  riskScore: number;
}

const ConversationPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sessionId, setSessionId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [summary, setSummary] = useState<QuestionnaireSummary | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const steps = ["Start Conversation", "Answer Questions", "Review Summary"];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startConversation = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await conversationAPI.start();
      const { session_id, response: agentResponse, agent_type } = response.data;

      setSessionId(session_id);
      setConversationStarted(true);
      setCurrentStep(1);

      // Add initial agent message
      const initialMessage: Message = {
        id: "1",
        text: agentResponse,
        sender: "agent",
        agentType: agent_type,
        timestamp: new Date(),
      };

      setMessages([initialMessage]);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to start conversation");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setLoading(true);

    try {
      const response = await conversationAPI.continue(inputMessage, sessionId);
      const {
        response: agentResponse,
        agent_type,
        emotional_state,
      } = response.data;

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: agentResponse,
        sender: "agent",
        agentType: agent_type,
        timestamp: new Date(),
        emotionalState: emotional_state,
      };

      setMessages((prev) => [...prev, agentMessage]);

      // Check if we should move to analysis phase
      if (agent_type === "adaptive_questionnaire" && messages.length > 5) {
        await analyzeTrends();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  const analyzeTrends = async () => {
    try {
      setLoading(true);
      const response = await conversationAPI.analyze();
      const { analysis } = response.data;

      // Create summary from analysis
      const questionnaireSummary: QuestionnaireSummary = {
        totalQuestions: analysis.data_points || 0,
        completedQuestions: analysis.data_points || 0,
        keyFindings: analysis.recommendations || [],
        recommendations: analysis.recommendations || [],
        riskScore: analysis.risk_score || 0,
      };

      setSummary(questionnaireSummary);
      setCurrentStep(2);
      setShowSummary(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to analyze trends");
    } finally {
      setLoading(false);
    }
  };

  const completeConversation = async () => {
    try {
      setLoading(true);
      const response = await conversationAPI.complete(sessionId);
      const { completion_message } = response.data;

      const completionMessage: Message = {
        id: Date.now().toString(),
        text: completion_message,
        sender: "agent",
        agentType: "companion",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, completionMessage]);
      setShowSummary(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to complete conversation");
    } finally {
      setLoading(false);
    }
  };

  const getAgentIcon = (agentType?: string) => {
    switch (agentType) {
      case "companion":
        return <Person color="primary" />;
      case "adaptive_questionnaire":
        return <Psychology color="secondary" />;
      case "trend_monitoring":
        return <TrendingUp color="success" />;
      default:
        return <SmartToy color="info" />;
    }
  };

  const getAgentColor = (agentType?: string) => {
    switch (agentType) {
      case "companion":
        return "primary";
      case "adaptive_questionnaire":
        return "secondary";
      case "trend_monitoring":
        return "success";
      default:
        return "info";
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          AI Health Conversation
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Interact with our multi-agent system for personalized health support
        </Typography>
      </Box>

      {/* Progress Stepper */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {!conversationStarted ? (
        /* Start Conversation Card */
        <Card>
          <CardContent sx={{ textAlign: "center", py: 4 }}>
            <Psychology sx={{ fontSize: 64, color: "primary.main", mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Ready to Start Your Health Check-in?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Our AI agents will guide you through a personalized health
              assessment and provide insights based on your responses.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={startConversation}
              disabled={loading}
              startIcon={
                loading ? <CircularProgress size={20} /> : <Psychology />
              }
            >
              {loading ? "Starting..." : "Start Conversation"}
            </Button>
          </CardContent>
        </Card>
      ) : (
        /* Conversation Interface */
        <Box>
          {/* Messages Area */}
          <Card sx={{ mb: 3, height: "500px", overflow: "hidden" }}>
            <CardContent
              sx={{ height: "100%", display: "flex", flexDirection: "column" }}
            >
              <Box sx={{ flexGrow: 1, overflow: "auto", mb: 2 }}>
                <List>
                  {messages.map((message, index) => (
                    <React.Fragment key={message.id}>
                      <ListItem
                        sx={{
                          flexDirection: "column",
                          alignItems:
                            message.sender === "user"
                              ? "flex-end"
                              : "flex-start",
                        }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            mb: 1,
                            maxWidth: "70%",
                          }}
                        >
                          {message.sender === "agent" && (
                            <Box sx={{ mr: 1 }}>
                              {getAgentIcon(message.agentType)}
                            </Box>
                          )}
                          <Paper
                            sx={{
                              p: 2,
                              bgcolor:
                                message.sender === "user"
                                  ? "primary.main"
                                  : "grey.100",
                              color:
                                message.sender === "user"
                                  ? "white"
                                  : "text.primary",
                              borderRadius: 2,
                            }}
                          >
                            <Typography variant="body1">
                              {message.text}
                            </Typography>
                            {message.agentType && (
                              <Chip
                                label={message.agentType.replace("_", " ")}
                                size="small"
                                color={getAgentColor(message.agentType) as any}
                                sx={{ mt: 1 }}
                              />
                            )}
                          </Paper>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {message.timestamp.toLocaleTimeString()}
                        </Typography>
                      </ListItem>
                      {index < messages.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                  <div ref={messagesEndRef} />
                </List>
              </Box>

              {/* Input Area */}
              <Box sx={{ display: "flex", gap: 1 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Type your message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                  disabled={loading}
                />
                <Button
                  variant="contained"
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || loading}
                  sx={{ minWidth: "auto", px: 3 }}
                >
                  {loading ? <CircularProgress size={20} /> : <Send />}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
            <Button
              variant="outlined"
              onClick={analyzeTrends}
              disabled={loading || messages.length < 3}
              startIcon={<TrendingUp />}
            >
              Analyze Trends
            </Button>
            <Button
              variant="contained"
              onClick={completeConversation}
              disabled={loading || !sessionId}
              startIcon={<CheckCircle />}
            >
              Complete Session
            </Button>
          </Box>
        </Box>
      )}

      {/* Summary Dialog */}
      <Dialog
        open={showSummary}
        onClose={() => setShowSummary(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <CheckCircle sx={{ mr: 1, color: "success.main" }} />
            <Typography variant="h6">Questionnaire Summary</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {summary && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Assessment Results
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Progress: {summary.completedQuestions} /{" "}
                  {summary.totalQuestions} questions completed
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={
                    (summary.completedQuestions / summary.totalQuestions) * 100
                  }
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Risk Assessment
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <Box sx={{ flexGrow: 1, mr: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={summary.riskScore * 100}
                      color={
                        summary.riskScore > 0.7
                          ? "error"
                          : summary.riskScore > 0.3
                          ? "warning"
                          : "success"
                      }
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                  <Chip
                    label={`${(summary.riskScore * 100).toFixed(0)}% Risk`}
                    color={
                      summary.riskScore > 0.7
                        ? "error"
                        : summary.riskScore > 0.3
                        ? "warning"
                        : "success"
                    }
                  />
                </Box>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Key Findings
                </Typography>
                <List dense>
                  {summary.keyFindings.map((finding, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={finding} />
                    </ListItem>
                  ))}
                </List>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                <List dense>
                  {summary.recommendations.map((rec, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))}
                </List>
              </Box>

              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Thank you for completing your health assessment! Your
                  responses have been analyzed by our AI agents. A summary has
                  been sent to your healthcare provider if any concerning trends
                  were detected.
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSummary(false)}>Close</Button>
          <Button variant="contained" onClick={completeConversation}>
            Complete Session
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConversationPage;
