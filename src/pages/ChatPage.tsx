import React, { useState, useEffect, useRef } from "react";
import { Send, Image, Bot } from "lucide-react";
import { apiService } from "../services/api";
import { Conversation, HealthMetrics } from "../types";
import { useAuth } from "../context/AuthContext";

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(
    null
  );
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [conversationResponse, metricsResponse] = await Promise.all([
          apiService.getConversations(),
          apiService.getHealthMetrics(),
        ]);

        if (
          conversationResponse.success &&
          conversationResponse.data &&
          conversationResponse.data.length > 0
        ) {
          setConversation(conversationResponse.data[0]);
        }

        if (metricsResponse.success && metricsResponse.data) {
          setHealthMetrics(metricsResponse.data);
        }
      } catch (error) {
        console.error("Error fetching chat data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newMessage.trim() || !conversation) return;

    setIsSending(true);
    const messageToSend = newMessage;
    setNewMessage("");

    try {
      const response = await apiService.sendMessage(
        conversation.id,
        messageToSend
      );

      if (response.success && response.data) {
        // Update conversation with new message
        setConversation((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            messages: [...prev.messages, response.data!],
            updatedAt: new Date(),
          };
        });

        // Simulate AI response after a delay
        setTimeout(async () => {
          const updatedConversation = await apiService.getConversation(
            conversation.id
          );
          if (updatedConversation.success && updatedConversation.data) {
            setConversation(updatedConversation.data);
          }
        }, 2000);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsSending(false);
    }
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(new Date(date));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading chat...</div>
      </div>
    );
  }

  return (
    <div className="gap-1 px-6 flex flex-1 justify-center py-5">
      <div className="layout-content-container flex flex-col max-w-[920px] flex-1">
        <div className="flex flex-wrap justify-between gap-3 p-4">
          <p className="text-gray-900 tracking-light text-[32px] font-bold leading-tight min-w-72">
            Chatbot
          </p>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 max-h-[600px]">
          {conversation?.messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-end gap-3 p-4 ${
                message.sender === "user" ? "justify-end" : ""
              }`}
            >
              {message.sender === "ai" && (
                <div
                  className="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0"
                  style={{
                    backgroundImage:
                      'url("https://lh3.googleusercontent.com/aida-public/AB6AXuA69fjVLbhmqDjCCKV7fZUKwG-8BO5SQNlDk5h0_YbXYwXrR0f7swKSgP_XpttlFdtvtPQzkpv5MWEzGJduMsFyE2_adExe_2IibjdGdU24pkIh4QgX6pquaXrhjya8oGyA-1m-wnvqO8iC79rDOHrg6OAGxuAykQKrqBz8Sjh03-AMsX4RumNQ6ZFBc37FAOX_sfcFQ7meh6nu1UriBdDcKZFWalYeP5g-M1mKqF0er5tM_tQVghxf9x5uiUx-H6tmMX8HAi01rv92")',
                  }}
                />
              )}

              <div
                className={`flex flex-1 flex-col gap-1 ${
                  message.sender === "user" ? "items-end" : "items-start"
                }`}
              >
                <p
                  className={`text-gray-500 text-[13px] font-normal leading-normal max-w-[360px] ${
                    message.sender === "user" ? "text-right" : ""
                  }`}
                >
                  {message.sender === "user"
                    ? user?.name || "You"
                    : "Dr. Emily Carter"}
                </p>
                <div
                  className={`text-base font-normal leading-normal flex max-w-[360px] rounded-lg px-4 py-3 ${
                    message.sender === "user"
                      ? "bg-primary-500 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  {message.content}
                </div>
                <span className="text-xs text-gray-400 mt-1">
                  {formatTime(message.timestamp)}
                </span>
              </div>

              {message.sender === "user" && (
                <div
                  className="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0"
                  style={{
                    backgroundImage: user?.avatar
                      ? `url(${user.avatar})`
                      : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  }}
                />
              )}
            </div>
          ))}

          {isSending && (
            <div className="flex items-end gap-3 p-4">
              <div
                className="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0"
                style={{
                  backgroundImage:
                    'url("https://lh3.googleusercontent.com/aida-public/AB6AXuA69fjVLbhmqDjCCKV7fZUKwG-8BO5SQNlDk5h0_YbXYwXrR0f7swKSgP_XpttlFdtvtPQzkpv5MWEzGJduMsFyE2_adExe_2IibjdGdU24pkIh4QgX6pquaXrhjya8oGyA-1m-wnvqO8iC79rDOHrg6OAGxuAykQKrqBz8Sjh03-AMsX4RumNQ6ZFBc37FAOX_sfcFQ7meh6nu1UriBdDcKZFWalYeP5g-M1mKqF0er5tM_tQVghxf9x5uiUx-H6tmMX8HAi01rv92")',
                }}
              />
              <div className="flex flex-1 flex-col gap-1 items-start">
                <p className="text-gray-500 text-[13px] font-normal leading-normal max-w-[360px]">
                  Dr. Emily Carter
                </p>
                <div className="bg-gray-100 text-gray-900 text-base font-normal leading-normal flex max-w-[360px] rounded-lg px-4 py-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <form
          onSubmit={handleSendMessage}
          className="flex items-center px-4 py-3 gap-3"
        >
          <div
            className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0"
            style={{
              backgroundImage: user?.avatar
                ? `url(${user.avatar})`
                : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            }}
          />
          <label className="flex flex-col min-w-40 h-12 flex-1">
            <div className="flex w-full flex-1 items-stretch rounded-lg h-full">
              <input
                type="text"
                placeholder="Type your message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                disabled={isSending}
                className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 border-none bg-gray-100 h-full placeholder:text-gray-500 px-4 rounded-r-none border-r-0 pr-2 text-base font-normal leading-normal disabled:opacity-50"
              />
              <div className="flex border-none bg-gray-100 items-center justify-center pr-4 rounded-r-lg border-l-0">
                <div className="flex items-center gap-4 justify-end">
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      className="flex items-center justify-center p-1.5 hover:bg-gray-200 rounded transition-colors"
                    >
                      <Image size={20} className="text-gray-500" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </label>
          <button
            type="submit"
            disabled={!newMessage.trim() || isSending}
            className="flex items-center justify-center p-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </form>
      </div>

      {/* Sidebar */}
      <div className="layout-content-container flex flex-col w-[360px]">
        <h2 className="text-gray-900 text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">
          Conversation Summary
        </h2>
        <p className="text-gray-900 text-base font-normal leading-normal pb-3 pt-1 px-4">
          {conversation?.summary || "No conversation summary available."}
        </p>

        <h2 className="text-gray-900 text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">
          Health Information
        </h2>
        <div className="flex flex-wrap gap-4 p-4">
          <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-6 border border-gray-200 bg-white">
            <p className="text-gray-900 text-base font-medium leading-normal">
              Heart Rate
            </p>
            <p className="text-gray-900 tracking-light text-2xl font-bold leading-tight">
              {healthMetrics?.heartRate} bpm
            </p>
          </div>
          <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-6 border border-gray-200 bg-white">
            <p className="text-gray-900 text-base font-medium leading-normal">
              Blood Pressure
            </p>
            <p className="text-gray-900 tracking-light text-2xl font-bold leading-tight">
              {healthMetrics?.bloodPressure.systolic}/
              {healthMetrics?.bloodPressure.diastolic} mmHg
            </p>
          </div>
          <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-6 border border-gray-200 bg-white">
            <p className="text-gray-900 text-base font-medium leading-normal">
              Sleep
            </p>
            <p className="text-gray-900 tracking-light text-2xl font-bold leading-tight">
              {healthMetrics?.sleep} hrs
            </p>
          </div>
        </div>

        {/* Agent Status */}
        <div className="px-4 py-4">
          <h3 className="text-gray-900 text-lg font-bold mb-3">
            Active Agents
          </h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Bot size={16} className="text-green-600" />
                <span className="text-sm font-medium text-gray-900">
                  Companion Agent
                </span>
              </div>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Active
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Bot size={16} className="text-blue-600" />
                <span className="text-sm font-medium text-gray-900">
                  Questionnaire Agent
                </span>
              </div>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                Active
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Bot size={16} className="text-purple-600" />
                <span className="text-sm font-medium text-gray-900">
                  Monitoring Agent
                </span>
              </div>
              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                Active
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
