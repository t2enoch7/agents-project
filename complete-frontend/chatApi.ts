export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
  timestamp: string;
}

export async function sendMessage(
  chatHistory: ChatMessage[],
  message: string
): Promise<ChatMessage> {
  // Simulate network delay
  await new Promise((r) => setTimeout(r, 1000));
  // Synthetic bot response
  return {
    sender: "bot",
    text: "This is a synthetic response. (Replace with real API call.)",
    timestamp: new Date().toISOString(),
  };
}
