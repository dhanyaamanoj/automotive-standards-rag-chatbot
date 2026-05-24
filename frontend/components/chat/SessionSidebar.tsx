"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { getSessions, deleteSession } from "@/lib/api";
import { Session } from "@/types";
import { formatTimestamp, truncate } from "@/lib/utils";

export default function SessionSidebar({ currentSessionId }: { currentSessionId: string }) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const router = useRouter();

  useEffect(() => {
    getSessions().then(setSessions).catch(() => setSessions([]));
  }, [currentSessionId]);

  const newChat = () => router.push(`/chat/${uuidv4()}`);

  const handleDelete = async (e: React.MouseEvent, sid: string) => {
    e.stopPropagation();
    await deleteSession(sid);
    setSessions(s => s.filter(x => x.session_id !== sid));
    if (sid === currentSessionId) newChat();
  };

  return (
    <div style={{
      width: 200, flexShrink: 0, borderRight: "1px solid #e9ecef",
      background: "#f8f9fa", display: "flex", flexDirection: "column",
      height: "100vh", overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{ padding: "14px 12px 8px", borderBottom: "1px solid #e9ecef" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontWeight: 600, fontSize: 13, color: "#212529" }}>AIS Chat</span>
          <a href="/documents" style={{ fontSize: 11, color: "#2563eb", textDecoration: "none" }}>Docs</a>
        </div>
        <button onClick={newChat} style={{
          width: "100%", marginTop: 8, fontSize: 12, padding: "6px 10px",
          background: "#2563eb", color: "white", border: "none", borderRadius: 6,
        }}>+ New chat</button>
      </div>

      {/* Session list */}
      <div style={{ flex: 1, overflowY: "auto", padding: "6px 6px" }}>
        <div style={{ fontSize: 10, color: "#868e96", padding: "4px 6px 4px", letterSpacing: "0.05em" }}>
          RECENT
        </div>
        {sessions.length === 0 && (
          <div style={{ fontSize: 12, color: "#868e96", padding: "8px 6px" }}>No sessions yet</div>
        )}
        {sessions.map(s => (
          <div
            key={s.session_id}
            onClick={() => router.push(`/chat/${s.session_id}`)}
            style={{
              padding: "7px 8px", borderRadius: 6, cursor: "pointer",
              background: s.session_id === currentSessionId ? "#eff6ff" : "transparent",
              border: s.session_id === currentSessionId ? "1px solid #bfdbfe" : "1px solid transparent",
              marginBottom: 2, position: "relative",
            }}
          >
            <div style={{ fontSize: 12, color: "#212529", lineHeight: 1.3 }}>
              {truncate(s.title, 28)}
            </div>
            <div style={{ fontSize: 10, color: "#868e96", marginTop: 2 }}>
              {formatTimestamp(s.timestamp)}
            </div>
            <button
              onClick={(e) => handleDelete(e, s.session_id)}
              style={{
                position: "absolute", right: 4, top: 6, width: 18, height: 18,
                padding: 0, fontSize: 11, background: "transparent", color: "#868e96",
                border: "none", borderRadius: 3, display: "none",
              }}
              className="del-btn"
            >×</button>
          </div>
        ))}
      </div>

      {/* Footer nav */}
      <div style={{ borderTop: "1px solid #e9ecef", padding: "8px 10px" }}>
        <a href="/dashboard" style={{
          display: "block", fontSize: 12, color: "#495057",
          textDecoration: "none", padding: "4px 0",
        }}>📊 Evaluation</a>
        <a href="/documents" style={{
          display: "block", fontSize: 12, color: "#495057",
          textDecoration: "none", padding: "4px 0",
        }}>📄 Documents</a>
      </div>
    </div>
  );
}
