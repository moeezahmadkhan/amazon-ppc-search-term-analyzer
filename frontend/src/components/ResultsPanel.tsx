"use client";

interface CategoryResult {
  name: string;
  count: number;
  totalClicks: number;
  totalSpend: number;
  totalOrders: number;
  avgAcos: number;
}

interface ResultsPanelProps {
  results: CategoryResult[] | null;
  isLoading: boolean;
}

const CATEGORY_STYLES: Record<string, { bg: string; border: string; icon: string; text: string }> = {
  "Wasted Adspend": {
    bg: "bg-danger/10",
    border: "border-danger/30",
    icon: "text-danger",
    text: "text-danger",
  },
  "Inefficient Adspend": {
    bg: "bg-warning/10",
    border: "border-warning/30",
    icon: "text-warning",
    text: "text-warning",
  },
  "Scaling Opportunity": {
    bg: "bg-success/10",
    border: "border-success/30",
    icon: "text-success",
    text: "text-success",
  },
  "Harvesting Opportunity": {
    bg: "bg-info/10",
    border: "border-info/30",
    icon: "text-info",
    text: "text-info",
  },
};

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  "Wasted Adspend": (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  ),
  "Inefficient Adspend": (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
    </svg>
  ),
  "Scaling Opportunity": (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v-5.5" />
    </svg>
  ),
  "Harvesting Opportunity": (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375" />
    </svg>
  ),
};

export default function ResultsPanel({ results, isLoading }: ResultsPanelProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-20 rounded-lg bg-card animate-pulse" />
        ))}
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center py-12 text-foreground/30">
        <svg className="w-16 h-16 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        </svg>
        <p className="text-sm">Upload a report and click Analyze to see results</p>
      </div>
    );
  }

  const totalTerms = results.reduce((s, r) => s + r.count, 0);

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center mb-1">
        <h2 className="text-lg font-semibold">Analysis Results</h2>
        <span className="text-sm text-foreground/50">{totalTerms} total terms flagged</span>
      </div>

      {results.map((cat) => {
        const style = CATEGORY_STYLES[cat.name] || CATEGORY_STYLES["Wasted Adspend"];
        const icon = CATEGORY_ICONS[cat.name];

        return (
          <div
            key={cat.name}
            className={`rounded-lg border p-4 ${style.bg} ${style.border} transition-all hover:scale-[1.01]`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={style.icon}>{icon}</span>
                <h3 className={`font-semibold ${style.text}`}>{cat.name}</h3>
              </div>
              <span className={`text-2xl font-bold font-mono ${style.text}`}>{cat.count}</span>
            </div>
            <div className="grid grid-cols-4 gap-3 text-xs text-foreground/60">
              <div>
                <p className="uppercase tracking-wider mb-0.5">Clicks</p>
                <p className="font-mono font-medium text-foreground/80">{cat.totalClicks.toLocaleString()}</p>
              </div>
              <div>
                <p className="uppercase tracking-wider mb-0.5">Spend</p>
                <p className="font-mono font-medium text-foreground/80">${cat.totalSpend.toFixed(2)}</p>
              </div>
              <div>
                <p className="uppercase tracking-wider mb-0.5">Orders</p>
                <p className="font-mono font-medium text-foreground/80">{cat.totalOrders.toLocaleString()}</p>
              </div>
              <div>
                <p className="uppercase tracking-wider mb-0.5">Avg ACOS</p>
                <p className="font-mono font-medium text-foreground/80">{(cat.avgAcos * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export type { CategoryResult };
