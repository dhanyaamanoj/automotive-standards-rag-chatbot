"use client";
import { useState } from "react";
import SessionSidebar from "@/components/chat/SessionSidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import DocumentPanel from "@/components/chat/DocumentPanel";
import { Citation } from "@/types";

export default function ChatPage({ params }: { params: { sessionId: string } }) {
  const { sessionId } = params;
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [activeScores, setActiveScores] = useState<Record<string, number>>({});

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      <SessionSidebar currentSessionId={sessionId} />
      <ChatWindow
        sessionId={sessionId}
        onCitationClick={(c, scores) => {
          setActiveCitation(c);
          setActiveScores(scores);
        }}
      />
      <DocumentPanel citation={activeCitation} scores={activeScores} />
    </div>
  );
}