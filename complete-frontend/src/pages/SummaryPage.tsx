import React from "react";
import { useChat } from "../context/ChatContext";
import { useLocation, useNavigate } from "react-router-dom";

export default function SummaryPage() {
  const { chat } = useChat();
  const location = useLocation();
  const navigate = useNavigate();
  // Questionnaire answers passed via location.state
  const answers: Record<string, string> = location.state?.answers || {};

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-6 text-center">
          Conversation Summary
        </h1>
        <h2 className="text-lg font-semibold mb-2">Chat</h2>
        <ul className="mb-4">
          {chat.map((msg, idx) => (
            <li key={idx} className="mb-2">
              <span
                className={`font-bold ${
                  msg.sender === "user" ? "text-blue-700" : "text-green-700"
                }`}
              >
                {msg.sender === "user" ? "You" : "Bot"}:
              </span>{" "}
              {msg.text}
            </li>
          ))}
        </ul>
        <h2 className="text-lg font-semibold mb-2">Questionnaire Answers</h2>
        <ul className="mb-4">
          {Object.entries(answers).map(([qid, ans]) => (
            <li key={qid} className="mb-2">
              <span className="font-medium">{qid}:</span> {ans}
            </li>
          ))}
        </ul>
        <button
          className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
          onClick={() => navigate("/")}
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}
