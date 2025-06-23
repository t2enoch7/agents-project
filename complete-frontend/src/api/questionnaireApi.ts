export type Questionnaire = {
  id: string;
  questions: { id: string; text: string; type: "text" | "choice"; options?: string[] }[];
};

export async function getQuestionnaire(): Promise<Questionnaire> {
  await new Promise((r) => setTimeout(r, 800));
  return {
    id: "q1",
    questions: [
      { id: "q1-1", text: "How many hours do you sleep per night?", type: "text" },
      { id: "q1-2", text: "Do you experience headaches?", type: "choice", options: ["Yes", "No"] },
      { id: "q1-3", text: "How would you rate your appetite?", type: "choice", options: ["Good", "Average", "Poor"] },
    ],
  };
}

export async function saveQuestionnaireAnswers(questionnaireId: string, answers: Record<string, string>): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  // No-op for synthetic
}
