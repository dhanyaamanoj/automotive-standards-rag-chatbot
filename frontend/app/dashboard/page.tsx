"use client";
import { useEffect, useState } from "react";
import { getEvalResults, triggerEvaluation } from "@/lib/api";
import { EvalResults } from "@/types";
import MetricCard from "@/components/evaluation/MetricCard";
import QATable from "@/components/evaluation/QATable";
import EvalChart from "@/components/evaluation/EvalChart";

export default function DashboardPage() {
  const [data, setData] = useState<EvalResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getEvalResults();
      // Validate the response has the expected structure
      if (result && typeof result === 'object') {
        setData(result);
      } else {
        setError("Invalid response format from API");
      }
    } catch (err) {
      console.error("Failed to fetch evaluation results:", err);
      setError("Failed to load evaluation results. Please ensure the backend is running and evaluation has been run.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      await triggerEvaluation();
      // Wait for evaluation to complete (adjust timing as needed)
      setTimeout(async () => {
        await fetchData();
        setRunning(false);
      }, 5000);
    } catch (err) {
      console.error("Failed to trigger evaluation:", err);
      setError("Failed to start evaluation. Check backend logs.");
      setRunning(false);
    }
  };

  // Safely extract metrics with fallbacks
  const safeMetrics = {
    avg_faithfulness: data?.avg_faithfulness ?? 0,
    avg_answer_relevance: data?.avg_answer_relevance ?? 0,
    avg_precision_at_5: data?.avg_precision_at_5 ?? 0,
    avg_recall_at_5: data?.avg_recall_at_5 ?? 0,
    avg_mrr: data?.avg_mrr ?? 0,
    total_questions: data?.total_questions ?? 0,
    rows: data?.rows ?? [],
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f8f9fa" }}>
      {/* Header */}
      <div style={{
        background: "#fff", borderBottom: "1px solid #e9ecef",
        padding: "14px 28px", display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div>
          <span style={{ fontWeight: 700, fontSize: 16 }}>Evaluation Dashboard</span>
          <a href="/chat/new" style={{ marginLeft: 16, fontSize: 13, color: "#2563eb", textDecoration: "none" }}>
            ← Back to chat
          </a>
        </div>
        <button 
          onClick={handleRun} 
          disabled={running} 
          style={{ 
            fontSize: 12, 
            padding: "7px 16px",
            background: running ? "#ccc" : "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: running ? "not-allowed" : "pointer",
          }}
        >
          {running ? "Running…" : "Run Evaluation"}
        </button>
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 28px" }}>
        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0", color: "#868e96" }}>
            <div style={{ fontSize: 32, marginBottom: 10 }}>⏳</div>
            <p>Loading evaluation results…</p>
          </div>
        )}

        {error && !loading && (
          <div style={{ 
            textAlign: "center", 
            padding: "60px 20px", 
            background: "#fff", 
            borderRadius: 10,
            border: "1px solid #fecaca",
            color: "#dc2626"
          }}>
            <div style={{ fontSize: 32, marginBottom: 10 }}>⚠️</div>
            <p style={{ marginBottom: 16 }}>{error}</p>
            <button 
              onClick={handleRun} 
              disabled={running}
              style={{ 
                padding: "8px 20px", 
                background: "#2563eb", 
                color: "#fff",
                border: "none",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              {running ? "Running…" : "Run Evaluation Now"}
            </button>
          </div>
        )}

        {!loading && !error && data && safeMetrics.total_questions === 0 && (
          <div style={{ textAlign: "center", padding: "60px 0", color: "#868e96" }}>
            <div style={{ fontSize: 32, marginBottom: 10 }}>📊</div>
            <p>No evaluation results found.</p>
            <button 
              onClick={handleRun} 
              disabled={running}
              style={{ 
                marginTop: 10, 
                padding: "8px 20px", 
                background: "#2563eb", 
                color: "#fff",
                border: "none",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              {running ? "Running…" : "Run Evaluation Now"}
            </button>
          </div>
        )}

        {!loading && !error && data && safeMetrics.total_questions > 0 && (
          <>
            {/* Metric cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 24 }}>
              <MetricCard label="Faithfulness"     value={safeMetrics.avg_faithfulness}    />
              <MetricCard label="Answer Relevance" value={safeMetrics.avg_answer_relevance} />
              <MetricCard label="Precision@5"      value={safeMetrics.avg_precision_at_5}   />
              <MetricCard label="Recall@5"         value={safeMetrics.avg_recall_at_5}      />
              <MetricCard label="MRR"              value={safeMetrics.avg_mrr}              />
            </div>

            {/* Chart */}
            {safeMetrics.rows && safeMetrics.rows.length > 0 && (
              <div style={{ background: "#fff", borderRadius: 10, border: "1px solid #e9ecef", padding: 20, marginBottom: 24 }}>
                <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 14 }}>Scores by Question Type</div>
                <EvalChart rows={safeMetrics.rows} />
              </div>
            )}

            {/* Table */}
            {safeMetrics.rows && safeMetrics.rows.length > 0 && (
              <div style={{ background: "#fff", borderRadius: 10, border: "1px solid #e9ecef", padding: 20 }}>
                <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 14 }}>
                  Sample Q&A Results ({safeMetrics.total_questions} questions)
                </div>
                <QATable rows={safeMetrics.rows} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}