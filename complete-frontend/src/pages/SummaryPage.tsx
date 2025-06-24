import React, { useEffect, useState } from "react";
import { useChat } from "../context/ChatContext";
import { useLocation, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { getQuestionnaire } from "../api/questionnaireApi";
import type { Questionnaire } from "../api/questionnaireApi";
import ActivityMonitor from "../components/ActivityMonitor";

export default function SummaryPage() {
  const { chat } = useChat();
  const location = useLocation();
  const navigate = useNavigate();
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  // Questionnaire answers passed via location.state
  const answers: Record<string, string> = location.state?.answers || {};

  // Print conversation history to console on component mount
  useEffect(() => {
    console.log("Conversation History:", chat);
  }, [chat]);

  // Fetch questionnaire to map question IDs to text for accessibility
  useEffect(() => {
    getQuestionnaire()
      .then(setQuestionnaire)
      .finally(() => setLoading(false));
  }, []);

  const getQuestionText = (id: string) => {
    return (
      questionnaire?.questions.find((q) => q.id === id)?.text ||
      `Question ${id}`
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <main
        className="flex-1 flex flex-col items-center justify-center p-4"
        aria-label="Summary main content"
      >
        <section
          className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-3xl"
          aria-label="Submission summary"
        >
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-4 text-gray-900">
              Submission Complete
            </h1>
            <p className="text-lg text-gray-700 mb-8">
              Thank you for using your HealthAI companion today. Your responses
              have been recorded.
            </p>
          </div>

          <h2 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">
            Your Responses
          </h2>
          {loading ? (
            <ActivityMonitor />
          ) : (
            <dl className="space-y-4">
              {Object.entries(answers).map(([qid, ans]) => (
                <div
                  key={qid}
                  className="grid grid-cols-1 md:grid-cols-3 gap-2"
                >
                  <dt className="font-semibold text-gray-800 md:col-span-1">
                    {getQuestionText(qid)}
                  </dt>
                  <dd className="text-gray-700 md:col-span-2">{ans}</dd>
                </div>
              ))}
            </dl>
          )}

          <button
            className="w-full mt-10 bg-blue-700 text-white py-3 rounded-lg font-bold text-lg hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:ring-offset-2"
            onClick={() => navigate("/")}
            aria-label="Back to Home"
          >
            Back to Home
          </button>
        </section>
      </main>
    </div>
  );
}
