// frontend/components/evaluation/MetricCard.tsx
"use client";

interface MetricCardProps {
  label: string;
  value: number | null | undefined;
  color?: string;
  bg?: string;
}

export default function MetricCard({ 
  label, 
  value, 
  color = "#2563eb", 
  bg = "#eff6ff" 
}: MetricCardProps) {
  // Safe check: if value is undefined, null, or not a number, show "--"
  const displayValue = (typeof value === 'number' && !isNaN(value)) 
    ? value.toFixed(2) 
    : "--";
  
  return (
    <div style={{ 
      background: bg, 
      borderRadius: 10, 
      padding: "16px 18px", 
      border: '1px solid rgba(0,0,0,0.05)' 
    }}>
      <div style={{ fontSize: 11, color: "#495057", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color }}>{displayValue}</div>
    </div>
  );
}