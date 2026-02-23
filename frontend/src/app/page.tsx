"use client";

import { useState, useCallback } from "react";
import FileUploader from "@/components/FileUploader";
import ThresholdSliders from "@/components/ThresholdSliders";
import type { Thresholds } from "@/components/ThresholdSliders";
import ResultsPanel from "@/components/ResultsPanel";
import type { CategoryResult } from "@/components/ResultsPanel";
import DownloadButtons from "@/components/DownloadButtons";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const DEFAULT_THRESHOLDS: Thresholds = {
  click_threshold: 10,
  acos_threshold: 0.3,
  cvr_threshold: 0.1,
  low_click_threshold: 10,
  order_threshold: 2,
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [thresholds, setThresholds] = useState<Thresholds>(DEFAULT_THRESHOLDS);
  const [results, setResults] = useState<CategoryResult[] | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((f: File) => {
    setFile(f);
    setResults(null);
    setSessionId(null);
    setError(null);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("thresholds", JSON.stringify(thresholds));

      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Server error: ${res.status}`);
      }

      const data = await res.json();
      setResults(data.categories);
      setSessionId(data.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  }, [file, thresholds]);

  const handleReset = useCallback(() => {
    setFile(null);
    setResults(null);
    setSessionId(null);
    setError(null);
    setThresholds(DEFAULT_THRESHOLDS);
  }, []);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-card-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">Amazon PPC Analyzer</h1>
              <p className="text-xs text-foreground/40">Search Term Report Analysis</p>
            </div>
          </div>
          {(file || results) && (
            <button
              onClick={handleReset}
              className="text-xs text-foreground/40 hover:text-foreground/70 transition-colors cursor-pointer"
            >
              Reset
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Upload + Sliders + Analyze */}
          <div className="lg:col-span-4 space-y-6">
            {/* Upload */}
            <div className="bg-card rounded-xl border border-card-border p-5">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9.75m0 0l2.25-2.25M9.75 15l2.25 2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                </svg>
                Upload Report
              </h2>
              <FileUploader onFileSelect={handleFileSelect} isLoading={isLoading} />
            </div>

            {/* Thresholds */}
            <div className="bg-card rounded-xl border border-card-border p-5">
              <ThresholdSliders thresholds={thresholds} onChange={setThresholds} />
            </div>

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={!file || isLoading}
              className={`
                w-full py-3.5 rounded-xl font-semibold text-sm tracking-wide
                transition-all duration-200
                ${!file || isLoading
                  ? "bg-card border border-card-border text-foreground/30 cursor-not-allowed"
                  : "bg-accent hover:bg-accent-hover text-white shadow-lg shadow-accent/25 cursor-pointer active:scale-[0.98]"
                }
              `}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing...
                </span>
              ) : (
                "Analyze Report"
              )}
            </button>

            {/* Error */}
            {error && (
              <div className="bg-danger/10 border border-danger/30 rounded-lg p-3 text-sm text-danger">
                {error}
              </div>
            )}

            {/* Downloads */}
            <div className="bg-card rounded-xl border border-card-border p-5">
              <DownloadButtons sessionId={sessionId} hasResults={!!results} apiBase={API_BASE} />
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="lg:col-span-8">
            <div className="bg-card rounded-xl border border-card-border p-6 min-h-[400px]">
              <ResultsPanel results={results} isLoading={isLoading} />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-card-border mt-16">
        <div className="max-w-7xl mx-auto px-6 py-4 text-center text-xs text-foreground/30">
          Amazon PPC Search Term Analyzer -- File-in, File-out utility. No data stored.
        </div>
      </footer>
    </div>
  );
}
