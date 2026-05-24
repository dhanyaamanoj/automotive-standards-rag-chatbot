"use client";
import { Citation } from "@/types";

interface Props {
  citation: Citation;
  scores: Record<string, number>;
  onCitationClick: (c: Citation, scores: Record<string, number>) => void;
}

export default function SourceChip({ citation, scores, onCitationClick }: Props) {
  const label = `${citation.std_id}${citation.clause_id ? " Cl." + citation.clause_id : ""} p.${citation.page}`;

  return (
    <a
      href={citation.pdf_url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => { e.preventDefault(); onCitationClick(citation, scores); window.open(citation.pdf_url, "_blank"); }}
      style={{
        fontSize: 11, padding: "3px 9px", borderRadius: 4,
        background: "#eff6ff", color: "#2563eb",
        border: "1px solid #bfdbfe", textDecoration: "none",
        cursor: "pointer", whiteSpace: "nowrap",
      }}
    >
      {label} →
    </a>
  );
}
