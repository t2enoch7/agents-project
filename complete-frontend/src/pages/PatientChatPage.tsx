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
  const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<
    string,
    string
  > | null>(null);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
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

  // Show questionnaire after the first user message
  useEffect(() => {
    if (
      !showQuestionnaire &&
      chat.length > 1 &&
      chat.some((msg, idx) => idx > 0 && msg.sender === "user")
    ) {
      setShowQuestionnaire(true);
    }
  }, [chat, showQuestionnaire]);

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
    setShowQuestionnaire(false);
    setLoading(false);
    resetChat();
    navigate("/summary", { state: { answers } });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <main
        className="flex-1 flex flex-col items-center justify-center"
        aria-label="Patient chat main content"
      >
        <section
          className="w-full max-w-2xl p-4"
          aria-label="Chat conversation"
          tabIndex={0}
        >
          {chat.map((msg, idx) => (
            <div
              key={idx}
              className={`mb-2 flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`rounded-lg px-4 py-2 max-w-[80%] break-words shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  msg.sender === "user"
                    ? "bg-blue-700 text-white"
                    : "bg-white text-gray-900 border border-gray-200"
                }`}
                tabIndex={0}
                aria-label={
                  msg.sender === "user" ? "Your message" : "Bot message"
                }
              >
                {msg.text}
              </div>
            </div>
          ))}
          {loading && <ActivityMonitor />}
          {/* Questionnaire is positioned within the chat window */}
          {showQuestionnaire && !questionnaireAnswers && (
            <section className="mt-6" aria-label="Health questionnaire">
              <QuestionnaireComponent onSubmit={handleQuestionnaireSubmit} />
            </section>
          )}
        </section>
        {/* Hide or disable chat input while questionnaire is visible and not yet submitted */}
        {(!showQuestionnaire || questionnaireAnswers) && (
          <section
            className="w-full max-w-2xl p-4 flex gap-2"
            aria-label="Chat input"
          >
            <input
              className="form-input flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type your message..."
              aria-label="Type your message"
              disabled={loading}
            />
            <button
              className="bg-blue-700 text-white px-6 py-3 rounded-lg font-bold text-lg hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50"
              onClick={handleSend}
              disabled={loading}
              aria-busy={loading}
            >
              Send
            </button>
          </section>
        )}
      </main>
    </div>
  );
}
