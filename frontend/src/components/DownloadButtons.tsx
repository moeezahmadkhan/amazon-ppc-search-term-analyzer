"use client";

interface DownloadButtonsProps {
  sessionId: string | null;
  hasResults: boolean;
  apiBase: string;
}

export default function DownloadButtons({ sessionId, hasResults, apiBase }: DownloadButtonsProps) {
  const disabled = !sessionId || !hasResults;

  const handleDownload = (type: "report" | "bulk") => {
    if (!sessionId) return;
    const url = `${apiBase}/api/download/${type}/${sessionId}`;
    window.open(url, "_blank");
  };

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
        </svg>
        Downloads
      </h2>

      <button
        onClick={() => handleDownload("report")}
        disabled={disabled}
        className={`
          w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium text-sm
          transition-all duration-200
          ${disabled
            ? "bg-card border border-card-border text-foreground/30 cursor-not-allowed"
            : "bg-accent hover:bg-accent-hover text-white shadow-lg shadow-accent/20 cursor-pointer active:scale-[0.98]"
          }
        `}
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
        Analysis Report (.xlsx)
      </button>

      <button
        onClick={() => handleDownload("bulk")}
        disabled={disabled}
        className={`
          w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium text-sm
          transition-all duration-200
          ${disabled
            ? "bg-card border border-card-border text-foreground/30 cursor-not-allowed"
            : "bg-danger/90 hover:bg-danger text-white shadow-lg shadow-danger/20 cursor-pointer active:scale-[0.98]"
          }
        `}
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
        </svg>
        Bulk Negation File (.csv)
      </button>

      {!disabled && (
        <p className="text-xs text-foreground/40 text-center mt-1">
          The negation file contains {" "}
          <span className="text-danger font-medium">Wasted Adspend</span> terms
          formatted for Amazon bulk upload.
        </p>
      )}
    </div>
  );
}
