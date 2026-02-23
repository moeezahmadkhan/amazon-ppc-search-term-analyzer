"use client";

import { useMemo, useState } from "react";

interface NlpFilterPanelProps {
  sessionId: string | null;
  apiBase: string;
}

interface ParsedCondition {
  column: string;
  operator: string;
  value: unknown;
}

interface NlpResponse {
  category: string;
  prompt: string;
  parsed_filter: {
    mode: "all" | "any";
    limit: number;
    conditions: ParsedCondition[];
  };
  matched_count: number;
  preview_rows: Record<string, unknown>[];
}

const DEFAULT_PROMPT = "Filter out terms with less than 5 clicks";

const CATEGORY_OPTIONS = [
  "All Categories",
  "Wasted Adspend",
  "Inefficient Adspend",
  "Scaling Opportunity",
  "Harvesting Opportunity",
];

export default function NlpFilterPanel({ sessionId, apiBase }: NlpFilterPanelProps) {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [category, setCategory] = useState("All Categories");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<NlpResponse | null>(null);

  const previewColumns = useMemo(() => {
    if (!result?.preview_rows?.length) return [] as string[];
    return Object.keys(result.preview_rows[0]).slice(0, 8);
  }, [result]);

  const canRun = !!sessionId && prompt.trim().length > 0;

  const runNlpFilter = async () => {
    if (!canRun || !sessionId) return;
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${apiBase}/api/nlp/filter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          prompt,
          category,
          model: "gpt-4.1-mini",
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || `NLP request failed (${res.status})`);
      }

      const data = (await res.json()) as NlpResponse;
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "NLP filter failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-card rounded-xl border border-card-border p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-1.813-2.846a4.5 4.5 0 01-1.341-3.387V6.75A2.25 2.25 0 018.096 4.5h7.808a2.25 2.25 0 012.25 2.25v5.767a4.5 4.5 0 01-1.34 3.386L15 18.75l-.813-2.846M9.75 9h4.5" />
          </svg>
          NLP Filter (MLend)
        </h2>
        <span className="text-xs text-foreground/40">OpenAI</span>
      </div>

      <p className="text-xs text-foreground/50">
        Type natural language. The backend converts it into a strict filter JSON, validates it against allowed columns/operators, and applies it safely (no eval/exec).
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="md:col-span-2">
          <label className="text-xs text-foreground/50">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            className="mt-1 w-full rounded-lg border border-card-border bg-background px-3 py-2 text-sm outline-none focus:border-accent"
            placeholder="e.g., Show terms with clicks >= 10 and ACOS > 40%"
          />
        </div>
        <div>
          <label className="text-xs text-foreground/50">Category Scope</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="mt-1 w-full rounded-lg border border-card-border bg-background px-3 py-2 text-sm outline-none focus:border-accent"
          >
            {CATEGORY_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>

          <button
            onClick={runNlpFilter}
            disabled={!canRun || isLoading}
            className={`mt-3 w-full py-2.5 rounded-lg text-sm font-semibold transition ${
              !canRun || isLoading
                ? "bg-card border border-card-border text-foreground/30 cursor-not-allowed"
                : "bg-accent hover:bg-accent-hover text-white"
            }`}
          >
            {isLoading ? "Running..." : "Run NLP Filter"}
          </button>
        </div>
      </div>

      {!sessionId && (
        <div className="text-xs text-warning/90 bg-warning/10 border border-warning/30 rounded-lg px-3 py-2">
          Analyze a file first to create a session, then NLP filtering becomes available.
        </div>
      )}

      {error && (
        <div className="text-xs text-danger bg-danger/10 border border-danger/30 rounded-lg px-3 py-2">{error}</div>
      )}

      {result && (
        <div className="space-y-3">
          <div className="rounded-lg border border-card-border p-3 bg-background/40">
            <p className="text-xs text-foreground/50 mb-1">Parsed Filter (Guardrailed JSON)</p>
            <pre className="text-xs overflow-x-auto text-foreground/80">{JSON.stringify(result.parsed_filter, null, 2)}</pre>
            <p className="text-xs mt-2 text-foreground/50">
              Matched rows: <span className="text-foreground font-semibold">{result.matched_count}</span>
            </p>
          </div>

          {result.preview_rows.length > 0 && (
            <div className="overflow-auto rounded-lg border border-card-border">
              <table className="min-w-full text-xs">
                <thead className="bg-background/70">
                  <tr>
                    {previewColumns.map((col) => (
                      <th key={col} className="px-3 py-2 text-left font-semibold text-foreground/70 whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.preview_rows.slice(0, 10).map((row, idx) => (
                    <tr key={idx} className="border-t border-card-border/60">
                      {previewColumns.map((col) => (
                        <td key={col} className="px-3 py-2 whitespace-nowrap text-foreground/85">
                          {String(row[col] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
