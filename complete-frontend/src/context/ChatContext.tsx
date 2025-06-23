import React, { createContext, useContext, useState, ReactNode } from "react";

export type ChatMessage = {
  sender: "user" | "bot";
  text: string;
  timestamp: string;
};

interface ChatContextType {
  chat: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  resetChat: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const addMessage = (msg: ChatMessage) => setChat((c) => [...c, msg]);
  const resetChat = () => setChat([]);
  return (
    <ChatContext.Provider value={{ chat, addMessage, resetChat }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within ChatProvider");
  return ctx;
};
