"use client";

import { useState, useEffect } from "react";
import { searchApi } from "@/services/api";

interface ReportItem {
  id: string;
  query: string;
  type: string;
  created_at: string;
  results_count: number;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async (q?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchApi.getReports(q);
      setReports(data.reports || []);
    } catch (err: any) {
      setError(err.message || "Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchReports(searchQuery);
  };

  return (
    <div className="w-full max-w-5xl flex flex-col gap-6 animate-fade-in">
      <div className="flex justify-between items-end border-b border-panel-border pb-4">
        <div>
          <h2 className="text-3xl font-mono font-bold tracking-tight text-foreground">
            INTELLIGENCE <span className="text-accent glow-text">ARCHIVE</span>
          </h2>
          <p className="text-gray-400 font-mono text-sm mt-1">
            Browse and search through past OSINT investigations stored in Elasticsearch.
          </p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex gap-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by target (e.g. google.com)"
          className="flex-1 bg-panel border border-panel-border text-foreground rounded px-4 py-2 font-mono focus:outline-none focus:border-accent transition-colors placeholder:text-gray-600"
        />
        <button
          type="submit"
          className="bg-accent/10 text-accent border border-accent rounded px-6 py-2 font-mono font-bold hover:bg-accent hover:text-background transition-all"
        >
          FILTER
        </button>
      </form>

      {error && (
        <div className="w-full bg-red-900/20 border border-red-500/50 text-red-400 p-4 rounded font-mono text-sm text-center">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-10 h-10 border-2 border-panel-border border-t-accent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="bg-panel border border-panel-border rounded-lg overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background border-b border-panel-border">
                <th className="p-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Target</th>
                <th className="p-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Type</th>
                <th className="p-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Date (UTC)</th>
                <th className="p-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Hits</th>
                <th className="p-4 font-mono text-xs text-gray-500 uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {reports.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-gray-500 font-mono">
                    No reports found.
                  </td>
                </tr>
              ) : (
                reports.map((report) => (
                  <tr key={report.id} className="border-b border-panel-border/50 hover:bg-background transition-colors">
                    <td className="p-4 font-mono text-foreground font-semibold">
                      {report.query}
                    </td>
                    <td className="p-4">
                      <span className="bg-accent/10 text-accent border border-accent/20 px-2 py-1 rounded text-xs font-mono uppercase">
                        {report.type}
                      </span>
                    </td>
                    <td className="p-4 font-mono text-sm text-gray-400">
                      {new Date(report.created_at).toLocaleString()}
                    </td>
                    <td className="p-4">
                      <span className={`font-mono font-bold ${report.results_count > 0 ? "text-accent" : "text-gray-500"}`}>
                        {report.results_count}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      {/* Placeholder button for viewing details */}
                      <button className="text-sm font-mono text-blue-400 hover:text-blue-300 hover:underline">
                        View JSON
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
