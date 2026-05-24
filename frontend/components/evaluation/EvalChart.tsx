"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { EvalRow } from "@/types";

export default function EvalChart({ rows }: { rows: EvalRow[] }) {
  const types = ["factual", "reasoning", "multi-hop"];
  const data = types.map(t => {
    const subset = rows.filter(r => r.type === t);
    const avg = (key: keyof EvalRow) =>
      subset.length ? +(subset.reduce((s, r) => s + (r[key] as number), 0) / subset.length).toFixed(2) : 0;
    return { name: t, Faithfulness: avg("faithfulness"), Relevance: avg("answer_relevance"), MRR: avg("mrr") };
  });

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f3f5" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="Faithfulness"  fill="#2563eb" radius={[4,4,0,0]} />
        <Bar dataKey="Relevance"     fill="#16a34a" radius={[4,4,0,0]} />
        <Bar dataKey="MRR"           fill="#d97706" radius={[4,4,0,0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
