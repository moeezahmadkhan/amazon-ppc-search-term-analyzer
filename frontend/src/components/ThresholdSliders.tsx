"use client";

interface Thresholds {
  click_threshold: number;
  acos_threshold: number;
  cvr_threshold: number;
  low_click_threshold: number;
  order_threshold: number;
}

interface ThresholdSlidersProps {
  thresholds: Thresholds;
  onChange: (thresholds: Thresholds) => void;
}

interface SliderConfig {
  key: keyof Thresholds;
  label: string;
  description: string;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
  color: string;
}

const SLIDERS: SliderConfig[] = [
  {
    key: "click_threshold",
    label: "Click Threshold (Wasted)",
    description: "Min clicks with 0 orders to flag as wasted",
    min: 1,
    max: 50,
    step: 1,
    format: (v) => `${v} clicks`,
    color: "text-danger",
  },
  {
    key: "acos_threshold",
    label: "ACOS Threshold (Inefficient)",
    description: "Min ACOS with orders to flag as inefficient",
    min: 0.05,
    max: 1.0,
    step: 0.05,
    format: (v) => `${(v * 100).toFixed(0)}%`,
    color: "text-warning",
  },
  {
    key: "cvr_threshold",
    label: "CVR Threshold (Scaling)",
    description: "Min conversion rate for scaling opportunities",
    min: 0.01,
    max: 0.5,
    step: 0.01,
    format: (v) => `${(v * 100).toFixed(0)}%`,
    color: "text-success",
  },
  {
    key: "low_click_threshold",
    label: "Low Click Threshold (Scaling)",
    description: "Max clicks to qualify as low-traction Exact term",
    min: 1,
    max: 30,
    step: 1,
    format: (v) => `${v} clicks`,
    color: "text-success",
  },
  {
    key: "order_threshold",
    label: "Order Threshold (Harvesting)",
    description: "Min orders for untargeted terms to flag for harvesting",
    min: 1,
    max: 20,
    step: 1,
    format: (v) => `${v} orders`,
    color: "text-info",
  },
];

export default function ThresholdSliders({ thresholds, onChange }: ThresholdSlidersProps) {
  const handleChange = (key: keyof Thresholds, value: number) => {
    onChange({ ...thresholds, [key]: value });
  };

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
        </svg>
        Thresholds
      </h2>

      {SLIDERS.map((s) => (
        <div key={s.key} className="space-y-1.5">
          <div className="flex justify-between items-baseline">
            <label className="text-sm font-medium">{s.label}</label>
            <span className={`text-sm font-mono font-semibold ${s.color}`}>
              {s.format(thresholds[s.key])}
            </span>
          </div>
          <input
            type="range"
            min={s.min}
            max={s.max}
            step={s.step}
            value={thresholds[s.key]}
            onChange={(e) => handleChange(s.key, parseFloat(e.target.value))}
            className="w-full"
          />
          <p className="text-xs text-foreground/40">{s.description}</p>
        </div>
      ))}
    </div>
  );
}

export type { Thresholds };
