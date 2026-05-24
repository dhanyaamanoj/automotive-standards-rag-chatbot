"use client";
import { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { sendMessage, getSessionHistory } from "@/lib/api";
import { Message, Citation } from "@/types";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

interface Props {
  sessionId: string;
  onCitationClick: (c: Citation, scores: Record<string, number>) => void;
}

export default function ChatWindow({ sessionId, onCitationClick }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isNew = sessionId === "new";

  useEffect(() => {
    setMessages([]);
    if (!isNew) {
      getSessionHistory(sessionId).then((history: any[]) => {
        const msgs: Message[] = history.map((h: any) => ({
          id: uuidv4(),
          role: h.role,
          content: h.content,
          citations: h.citations || [],
          scores: {},
          timestamp: Date.now(),
        }));
        setMessages(msgs);
      }).catch(() => {});
    }
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");

    const userMsg: Message = {
      id: uuidv4(), role: "user", content: q,
      citations: [], scores: {}, timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const sid = isNew ? uuidv4() : sessionId;
      const data = await sendMessage(sid, q);
      const aiMsg: Message = {
        id: uuidv4(), role: "assistant",
        content: data.answer,
        citations: data.citations || [],
        scores: data.scores || {},
        query_type: data.query_type,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, aiMsg]);
      if (isNew && typeof window !== "undefined") {
        window.history.replaceState(null, "", `/chat/${sid}`);
      }
    } catch {
      setMessages(prev => [...prev, {
        id: uuidv4(), role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
        citations: [], scores: {}, timestamp: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      {/* Topbar */}
      <div style={{
        padding: "10px 18px", borderBottom: "1px solid #e9ecef",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "#fff", flexShrink: 0,
      }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>AIS Standards Assistant</span>
        <span style={{
          fontSize: 11, background: "#f0fdf4", color: "#16a34a",
          padding: "2px 10px", borderRadius: 20, border: "1px solid #bbf7d0",
        }}>Ready</span>
      </div>

      {/* Welcome */}
      {messages.length === 0 && (
        <div style={{ padding: "40px 24px", textAlign: "center", color: "#868e96" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>📋</div>
          <div style={{ fontSize: 15, fontWeight: 500, color: "#212529", marginBottom: 6 }}>
            Ask anything about AIS Standards
          </div>
          <div style={{ fontSize: 13 }}>
            Try: "What are the set speed tolerance requirements in AIS-018?"
          </div>
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "16px 18px", display: "flex", flexDirection: "column", gap: 12 }}>
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} onCitationClick={onCitationClick} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: "12px 18px", borderTop: "1px solid #e9ecef",
        background: "#fff", flexShrink: 0, display: "flex", gap: 8,
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Ask about AIS automotive standards..."
          style={{ flex: 1, fontSize: 13, padding: "9px 12px" }}
          disabled={loading}
        />
        <button onClick={submit} disabled={loading || !input.trim()}
          style={{ padding: "9px 18px", fontSize: 13, opacity: loading || !input.trim() ? 0.5 : 1 }}>
          Send
        </button>
      </div>
    </div>
  );
}
