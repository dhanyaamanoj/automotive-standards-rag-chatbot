"use client";
import { useEffect, useState } from "react";
import { getDocuments } from "@/lib/api";
import { DocumentMeta } from "@/types";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDocuments().then(setDocs).catch(() => setDocs([])).finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#f8f9fa" }}>
      <div style={{
        background: "#fff", borderBottom: "1px solid #e9ecef",
        padding: "14px 28px", display: "flex", alignItems: "center", gap: 16,
      }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Loaded Documents</span>
        <a href="/chat/new" style={{ fontSize: 13, color: "#2563eb", textDecoration: "none" }}>← Back to chat</a>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "24px 28px" }}>
        {loading && <p style={{ color: "#868e96" }}>Loading…</p>}
        {!loading && docs.length === 0 && (
          <div style={{ textAlign: "center", padding: "60px 0", color: "#868e96" }}>
            <div style={{ fontSize: 32 }}>📂</div>
            <p>No documents loaded yet. Run <code>python scripts/ingest.py</code> first.</p>
          </div>
        )}
        <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fill, minmax(260px,1fr))" }}>
          {docs.map(d => (
            <div key={d.std_id} style={{
              background: "#fff", border: "1px solid #e9ecef",
              borderRadius: 10, padding: "16px 18px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 700, fontSize: 15 }}>{d.std_id}</span>
                {d.is_amended && (
                  <span style={{
                    fontSize: 10, background: "#fef9c3", color: "#854d0e",
                    padding: "2px 7px", borderRadius: 20, border: "1px solid #fde047",
                  }}>Amended</span>
                )}
              </div>
              <div style={{ fontSize: 12, color: "#495057", marginTop: 8 }}>
                {d.chunk_count} chunks
              </div>
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 8 }}>
                {d.chunk_types.map(t => (
                  <span key={t} style={{
                    fontSize: 10, background: "#eff6ff", color: "#2563eb",
                    padding: "2px 7px", borderRadius: 20, border: "1px solid #bfdbfe",
                  }}>{t}</span>
                ))}
              </div>
              <a
                href={d.pdf_url ?? `/static/pdfs/${d.std_id}.pdf`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: 12, color: "#2563eb", textDecoration: "none", display: "block", marginTop: 10 }}
              >
                View PDF →
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
