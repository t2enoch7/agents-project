import React, { useEffect, useState } from "react";
import { useChat } from "../context/ChatContext";
import ActivityMonitor from "../components/ActivityMonitor";
import { sendMessage } from "../api/chatApi";
import QuestionnaireComponent from "../components/Questionnaire";
import { saveQuestionnaireAnswers } from "../api/questionnaireApi";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";

export default function PatientChatPage() {
  const { chat, addMessage, resetChat } = useChat();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
  const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<
    string,
    string
  > | null>(null);
  const navigate = useNavigate();

  // On first load, prompt the user
  useEffect(() => {
    if (chat.length === 0) {
      addMessage({
        sender: "bot",
        text: "How are you today?",
        timestamp: new Date().toISOString(),
      });
    }
  }, [chat, addMessage]);

  // After first user message, show questionnaire
  useEffect(() => {
    if (chat.length === 2 && chat[1].sender === "user") {
      setShowQuestionnaire(true);
    }
  }, [chat]);

  const handleSend = async () => {
    if (!input.trim()) return;
    addMessage({
      sender: "user",
      text: input,
      timestamp: new Date().toISOString(),
    });
    setLoading(true);
    const botMsg = await sendMessage(
      [
        ...chat,
        { sender: "user", text: input, timestamp: new Date().toISOString() },
      ],
      input
    );
    addMessage(botMsg);
    setInput("");
    setLoading(false);
  };

  const handleQuestionnaireSubmit = async (answers: Record<string, string>) => {
    setLoading(true);
    await saveQuestionnaireAnswers("q1", answers);
    setQuestionnaireAnswers(answers);
    setLoading(false);
    resetChat();
    navigate("/summary", { state: { answers } });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col items-center justify-center">
        <div className="w-full max-w-2xl p-4">
          {chat.map((msg, idx) => (
            <div
              key={idx}
              className={`mb-2 flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`rounded-lg px-4 py-2 ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {loading && <ActivityMonitor />}
        </div>
        {!showQuestionnaire && (
          <div className="w-full max-w-2xl p-4 flex gap-2">
            <input
              className="form-input flex-1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type your message..."
              aria-label="Type your message"
              disabled={loading}
            />
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold"
              onClick={handleSend}
              disabled={loading}
              aria-busy={loading}
            >
              Send
            </button>
          </div>
        )}
        {showQuestionnaire && !questionnaireAnswers && (
          <div className="w-full max-w-2xl p-4">
            <QuestionnaireComponent onSubmit={handleQuestionnaireSubmit} />
          </div>
        )}
      </main>
    </div>
  );
}
