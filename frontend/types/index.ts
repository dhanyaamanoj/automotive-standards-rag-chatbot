export interface Citation {
  std_id: string;
  clause_id: string;
  page: number;
  pdf_url: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  scores?: { faithfulness?: number; answer_relevance?: number };
  query_type?: string;
  timestamp: number;
}

export interface Session {
  session_id: string;
  title: string;
  timestamp: number;
}

export interface DocumentMeta {
  std_id: string;
  chunk_count: number;
  chunk_types: string[];
  is_amended: boolean;
  pdf_url?: string;
}

// export interface EvalRow {
//   query: string;
//   expected: string;
//   generated: string;
//   faithfulness: number;
//   answer_relevance: number;
//   precision_at_k: number;
//   recall_at_k: number;
//   mrr: number;
//   type: string;
//   difficulty: string;
// }

// export interface EvalResults {
//   total_questions: number;
//   avg_faithfulness: number;
//   avg_answer_relevance: number;
//   avg_precision_at_5: number;
//   avg_recall_at_5: number;
//   avg_mrr: number;
//   rows: EvalRow[];
// }
// Ensure your EvalResults type matches the backend response

export interface EvalRow {
  query: string;
  expected: string;
  generated: string;
  faithfulness: number;
  answer_relevance: number;
  precision_at_k: number;
  recall_at_k: number;
  mrr: number;
  type: string;
  difficulty: string;
}

export interface EvalResults {
  total_questions: number;
  avg_faithfulness: number;
  avg_answer_relevance: number;
  avg_precision_at_5: number;
  avg_recall_at_5: number;
  avg_mrr: number;
  rows: EvalRow[];
}