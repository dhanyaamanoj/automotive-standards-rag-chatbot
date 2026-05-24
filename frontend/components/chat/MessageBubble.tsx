"use client";
import { Message, Citation } from "@/types";
import SourceChip from "./SourceChip";

interface Props {
  message: Message;
  onCitationClick: (c: Citation, scores: Record<string, number>) => void;
}

export default function MessageBubble({ message, onCitationClick }: Props) {
  const isUser = message.role === "user";
  const isGrounded = message.citations && message.citations.length > 0;

  return (
    <div style={{
      display: "flex", gap: 10, alignItems: "flex-start",
      flexDirection: isUser ? "row-reverse" : "row",
    }}>
      {/* Avatar */}
      <div style={{
        width: 30, height: 30, borderRadius: "50%", flexShrink: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 12, fontWeight: 600,
        background: isUser ? "#e2e8f0" : "#eff6ff",
        color: isUser ? "#475569" : "#2563eb",
      }}>
        {isUser ? "U" : "AI"}
      </div>

      <div style={{ maxWidth: "78%", display: "flex", flexDirection: "column", gap: 4 }}>
        {/* Grounded badge */}
        {!isUser && isGrounded && (
          <span style={{
            fontSize: 10, background: "#f0fdf4", color: "#16a34a",
            padding: "2px 8px", borderRadius: 20, alignSelf: "flex-start",
            border: "1px solid #bbf7d0",
          }}>
            ✓ Grounded response
          </span>
        )}

        {/* Bubble */}
        <div style={{
          background: isUser ? "#2563eb" : "#f8f9fa",
          color: isUser ? "white" : "#212529",
          padding: "10px 14px", borderRadius: 10,
          fontSize: 13, lineHeight: 1.6,
          border: isUser ? "none" : "1px solid #e9ecef",
          whiteSpace: "pre-wrap",
        }}>
          {message.content}
        </div>

        {/* Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginTop: 2 }}>
            {message.citations.map((c, i) => (
              <SourceChip
                key={i}
                citation={c}
                scores={message.scores || {}}
                onCitationClick={onCitationClick}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
