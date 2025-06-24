export type Questionnaire = {
  id: string;
  questions: { id: string; text: string; type: "text" | "choice"; options?: string[] }[];
};

export async function getQuestionnaire(): Promise<Questionnaire> {
  await new Promise((r) => setTimeout(r, 800));
  return {
    id: "q1",
    questions: [
      {
        id: "q1-1",
        text: "How would you rate your overall energy level today?",
        type: "choice",
        options: ["Excellent", "Good", "Fair", "Poor"]
      },
      {
        id: "q1-2",
        text: "Have you experienced any pain or discomfort recently?",
        type: "choice",
        options: ["No", "Mild", "Moderate", "Severe"]
      },
      {
        id: "q1-3",
        text: "How many hours did you sleep last night?",
        type: "text"
      },
      {
        id: "q1-4",
        text: "Are you currently taking any medications? If yes, please list them.",
        type: "text"
      },
      {
        id: "q1-5",
        text: "Is there anything else you would like your care team to know today?",
        type: "text"
      }
    ],
  };
}

export async function saveQuestionnaireAnswers(questionnaireId: string, answers: Record<string, string>): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  // No-op for synthetic
}
