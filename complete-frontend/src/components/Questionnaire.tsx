import React, { useEffect, useState } from "react";
import { getQuestionnaire, Questionnaire } from "../api/questionnaireApi";
import ActivityMonitor from "./ActivityMonitor";

export default function QuestionnaireComponent({
  onSubmit,
}: {
  onSubmit: (answers: Record<string, string>) => void;
}) {
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(
    null
  );
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getQuestionnaire().then((q) => {
      setQuestionnaire(q);
      setLoading(false);
    });
  }, []);

  if (loading) return <ActivityMonitor />;
  if (!questionnaire)
    return <div className="text-red-600">Failed to load questionnaire.</div>;

  const handleChange = (id: string, value: string) => {
    setAnswers((a) => ({ ...a, [id]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(answers);
  };

  return (
    <form
      className="bg-white p-6 rounded-lg shadow w-full max-w-lg"
      onSubmit={handleSubmit}
      aria-label="Questionnaire form"
    >
      <h2 className="text-xl font-bold mb-4">Questionnaire</h2>
      {questionnaire.questions.map((q) => (
        <div className="mb-4" key={q.id}>
          <label className="block mb-2 font-medium" htmlFor={q.id}>
            {q.text}
          </label>
          {q.type === "text" ? (
            <input
              id={q.id}
              className="form-input w-full"
              value={answers[q.id] || ""}
              onChange={(e) => handleChange(q.id, e.target.value)}
              required
            />
          ) : (
            <select
              id={q.id}
              className="form-select w-full"
              value={answers[q.id] || ""}
              onChange={(e) => handleChange(q.id, e.target.value)}
              required
            >
              <option value="" disabled>
                Select an option
              </option>
              {q.options?.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          )}
        </div>
      ))}
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        Submit
      </button>
    </form>
  );
}
