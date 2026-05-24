export default function TypingIndicator() {
  return (
    <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
      <div style={{
        width: 30, height: 30, borderRadius: "50%",
        background: "#eff6ff", color: "#2563eb",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 12, fontWeight: 600, flexShrink: 0,
      }}>AI</div>
      <div style={{
        background: "#f8f9fa", border: "1px solid #e9ecef",
        borderRadius: 10, padding: "10px 16px",
        display: "flex", gap: 4, alignItems: "center",
      }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 6, height: 6, borderRadius: "50%", background: "#868e96",
            animation: "blink 1.2s infinite",
            animationDelay: `${i * 0.2}s`,
          }} />
        ))}
        <style>{`@keyframes blink { 0%,80%,100%{opacity:.2} 40%{opacity:1} }`}</style>
      </div>
    </div>
  );
}
