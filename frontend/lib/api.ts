import axios from "axios";
import type { Session, DocumentMeta, EvalResults } from "@/types";

const api = axios.create({ baseURL: "/api" });

export async function sendMessage(session_id: string, query: string) {
  const { data } = await api.post("/chat", { session_id, query });
  return data;
}

export async function getSessions(): Promise<Session[]> {
  const { data } = await api.get("/sessions");
  return data;
}

export async function getSessionHistory(session_id: string) {
  const { data } = await api.get(`/sessions/${session_id}`);
  return data;
}

export async function deleteSession(session_id: string) {
  await api.delete(`/sessions/${session_id}`);
}

export async function getDocuments(): Promise<DocumentMeta[]> {
  const { data } = await api.get("/documents");
  return data;
}

export async function getEvalResults(): Promise<EvalResults> {
  const { data } = await api.get("/evaluation/results");
  return data;
}

export async function triggerEvaluation() {
  const { data } = await api.post("/evaluation/run");
  return data;
}
