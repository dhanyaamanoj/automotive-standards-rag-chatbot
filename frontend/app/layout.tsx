import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AIS Standards Chatbot",
  description: "Multi-agent RAG chatbot for ARAI Automotive Industry Standards",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
