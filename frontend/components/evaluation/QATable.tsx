"use client";
import { useState } from "react";
import { EvalRow } from "@/types";

export default function QATable({ rows }: { rows: EvalRow[] }) {
  const [page, setPage] = useState(0);
  const PER_PAGE = 10;
  const paged = rows.slice(page * PER_PAGE, (page + 1) * PER_PAGE);
  const total = Math.ceil(rows.length / PER_PAGE);

  const scoreStyle = (v: number) => ({
    fontWeight: 600 as const,
    color: v >= 0.8 ? "#16a34a" : v >= 0.6 ? "#d97706" : "#dc2626",
  });

  return (
    <div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ background: "#f8f9fa", borderBottom: "2px solid #e9ecef" }}>
              {["Query","Type","Difficulty","Faithful","Relevance","Prec@5","Recall@5","MRR"]
                .map(h => <th key={h} style={{ padding: "8px 10px", textAlign: "left", color: "#495057", fontWeight: 600, whiteSpace: "nowrap" }}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {paged.map((r, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #f1f3f5" }}>
                <td style={{ padding: "8px 10px", maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={r.query}>{r.query}</td>
                <td style={{ padding: "8px 10px", color: "#495057" }}>{r.type}</td>
                <td style={{ padding: "8px 10px", color: "#495057" }}>{r.difficulty}</td>
                <td style={{ padding: "8px 10px", ...scoreStyle(r.faithfulness) }}>{r.faithfulness.toFixed(2)}</td>
                <td style={{ padding: "8px 10px", ...scoreStyle(r.answer_relevance) }}>{r.answer_relevance.toFixed(2)}</td>
                <td style={{ padding: "8px 10px", ...scoreStyle(r.precision_at_k) }}>{r.precision_at_k.toFixed(2)}</td>
                <td style={{ padding: "8px 10px", ...scoreStyle(r.recall_at_k) }}>{r.recall_at_k.toFixed(2)}</td>
                <td style={{ padding: "8px 10px", ...scoreStyle(r.mrr) }}>{r.mrr.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {total > 1 && (
        <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
          <button className="ghost" onClick={() => setPage(p => Math.max(0, p-1))} disabled={page === 0} style={{ fontSize: 12, padding: "4px 10px" }}>←</button>
          <span style={{ fontSize: 12, color: "#495057" }}>Page {page+1} of {total}</span>
          <button className="ghost" onClick={() => setPage(p => Math.min(total-1, p+1))} disabled={page === total-1} style={{ fontSize: 12, padding: "4px 10px" }}>→</button>
        </div>
      )}
    </div>
  );
}
