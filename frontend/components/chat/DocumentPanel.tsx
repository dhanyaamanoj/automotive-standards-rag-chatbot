"use client";
import { Citation } from "@/types";
import { scoreColor } from "@/lib/utils";

interface Props {
  citation: Citation | null;
  scores: Record<string, number>;
}

export default function DocumentPanel({ citation, scores }: Props) {
  return (
    <div style={{
      width: 240, flexShrink: 0, borderLeft: "1px solid #e9ecef",
      background: "#fff", display: "flex", flexDirection: "column",
      height: "100vh", overflow: "hidden",
    }}>
      <div style={{ padding: "12px 14px", borderBottom: "1px solid #e9ecef" }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: "#868e96", letterSpacing: "0.05em" }}>
          REFERENCE PANEL
        </div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px", display: "flex", flexDirection: "column", gap: 14 }}>
        {!citation ? (
          <div style={{ fontSize: 12, color: "#868e96", marginTop: 20 }}>
            Click a citation chip to view the referenced clause here.
          </div>
        ) : (
          <>
            {/* Clause card */}
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: "#495057", marginBottom: 6 }}>
                CITED CLAUSE
              </div>
              <div style={{
                border: "1px solid #e9ecef", borderRadius: 8, overflow: "hidden",
              }}>
                <div style={{
                  background: "#f8f9fa", padding: "7px 10px",
                  fontSize: 12, fontWeight: 500, color: "#212529",
                  borderBottom: "1px solid #e9ecef",
                }}>
                  {citation.std_id}
                  {citation.clause_id && ` — Cl. ${citation.clause_id}`}
                </div>
                <div style={{ padding: "8px 10px", fontSize: 12, color: "#495057", lineHeight: 1.6 }}>
                  <span style={{ background: "#fef9c3", borderRadius: 2, padding: "0 2px" }}>
                    Page {citation.page}
                  </span>
                  <br />
                  <a
                    href={citation.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#2563eb", fontSize: 12, textDecoration: "none", marginTop: 6, display: "inline-block" }}
                  >
                    Open in PDF →
                  </a>
                </div>
              </div>
            </div>

            {/* Scores */}
            {Object.keys(scores).length > 0 && (
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: "#495057", marginBottom: 6 }}>
                  QUALITY SCORES
                </div>
                {Object.entries(scores).map(([k, v]) => (
                  <div key={k} style={{
                    display: "flex", justifyContent: "space-between",
                    padding: "5px 0", borderBottom: "1px solid #f1f3f5",
                    fontSize: 12,
                  }}>
                    <span style={{ color: "#495057", textTransform: "capitalize" }}>
                      {k.replace(/_/g, " ")}
                    </span>
                    <span style={{
                      fontWeight: 600,
                      color: typeof v === "number"
                        ? v >= 0.8 ? "#16a34a" : v >= 0.6 ? "#d97706" : "#dc2626"
                        : "#212529",
                    }}>
                      {typeof v === "number" ? v.toFixed(2) : v}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
