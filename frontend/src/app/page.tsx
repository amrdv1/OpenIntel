"use client";

import { useState } from "react";
import { searchApi } from "@/services/api";
import { useTaskPolling } from "@/hooks/useTaskPolling";
import { SearchResult } from "@/types";

export default function Home() {
  const [query, setQuery] = useState("");
  const [queryType, setQueryType] = useState("email");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { status: pollStatus, results, error: pollError } = useTaskPolling(taskId);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    setIsSubmitting(true);
    setSubmitError(null);
    setTaskId(null);

    try {
      const res = await searchApi.startSearch(query, queryType);
      setTaskId(res.task_id);
    } catch (err: any) {
      setSubmitError(err.message || "Failed to start search");
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderResults = () => {
    if (pollStatus === "pending") {
      return (
        <div className="w-full mt-8 flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 border-4 border-panel-border border-t-accent rounded-full animate-spin"></div>
          <p className="text-accent font-mono glow-text animate-pulse">
            ANALYZING GLOBAL INTELLIGENCE NETWORKS...
          </p>
        </div>
      );
    }

    if (pollStatus === "completed" && results) {
      if (results.length === 0) {
        return (
          <div className="w-full mt-8 bg-panel border border-panel-border p-6 rounded text-center">
            <p className="text-gray-400 font-mono">No intelligence found for the given target.</p>
          </div>
        );
      }

      return (
        <div className="w-full mt-8 space-y-6">
          <h3 className="text-xl font-mono font-bold text-foreground border-b border-panel-border pb-2">
            INTELLIGENCE REPORT
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {results.map((res: SearchResult, idx: number) => (
              <div 
                key={idx} 
                className={`bg-panel border rounded p-5 flex flex-col gap-3 ${
                  res.status === "error" ? "border-red-900/50" : "border-accent/30 glow-box"
                }`}
              >
                <div className="flex justify-between items-start">
                  <span className="bg-background px-2 py-1 rounded text-xs font-mono font-bold text-gray-300 uppercase border border-panel-border">
                    {res.source}
                  </span>
                  <span className={`text-xs font-mono uppercase ${res.status === "error" ? "text-red-500" : "text-accent"}`}>
                    {res.status}
                  </span>
                </div>
                
                {res.status !== "error" ? (
                  <>
                    <h4 className="font-mono text-lg font-semibold text-white">{res.title || "Unknown Entity"}</h4>
                    {res.profile_url && (
                      <a 
                        href={res.profile_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="text-sm text-blue-400 hover:text-blue-300 truncate font-mono"
                      >
                        {res.profile_url}
                      </a>
                    )}
                    <p className="text-sm text-gray-400 font-sans mt-2">
                      {res.summary || "No summary available."}
                    </p>
                    <div className="mt-4">
                      <div className="flex justify-between text-xs font-mono text-gray-500 mb-1">
                        <span>CONFIDENCE</span>
                        <span>{Math.round(res.confidence * 100)}%</span>
                      </div>
                      <div className="w-full bg-background rounded h-1.5 overflow-hidden">
                        <div 
                          className="bg-accent h-full" 
                          style={{ width: `${res.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-red-400 font-mono mt-2">
                    {res.error_message || "Unknown error occurred while parsing source."}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }

    return null;
  };

  const error = submitError || pollError;

  return (
    <div className="w-full max-w-5xl flex flex-col items-center gap-8 animate-fade-in pb-16 relative">
      
      {/* Background Cyber Grid */}
      <div className="absolute inset-0 z-[-1] opacity-10 bg-[linear-gradient(rgba(0,255,157,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,157,0.1)_1px,transparent_1px)] bg-[size:40px_40px]"></div>

      <div className="text-center space-y-4 mt-8 relative">
        <div className="absolute -top-10 -left-10 w-20 h-20 bg-accent/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-10 -right-10 w-20 h-20 bg-blue-500/20 rounded-full blur-3xl"></div>
        <h2 className="text-5xl font-mono font-bold tracking-tighter text-foreground glitch-effect" data-text="OPENINTEL TERMINAL">
          OPENINTEL <span className="text-accent glow-text">TERMINAL</span>
        </h2>
        <p className="text-gray-400 font-mono text-sm max-w-xl mx-auto border-l-2 border-accent pl-4 text-left">
          <span className="text-accent">{">"}</span> INITIALIZING CONNECTION...<br/>
          <span className="text-accent">{">"}</span> ENTER TARGET IDENTIFIER FOR DEEP WEB RECONNAISSANCE.
        </p>
      </div>

      <form 
        onSubmit={handleSearch}
        className="w-full max-w-3xl bg-panel border border-panel-border rounded-lg p-6 flex flex-col gap-4 glow-box transition-all"
      >
        <div className="flex flex-col sm:flex-row gap-4">
          <select 
            value={queryType}
            onChange={(e) => setQueryType(e.target.value)}
            disabled={isSubmitting || pollStatus === "pending"}
            className="bg-background border border-panel-border text-foreground rounded px-4 py-3 font-mono focus:outline-none focus:border-accent transition-colors disabled:opacity-50"
          >
            <option value="email">EMAIL</option>
            <option value="username">USERNAME</option>
            <option value="domain">DOMAIN</option>
            <option value="phone">PHONE</option>
          </select>
          
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isSubmitting || pollStatus === "pending"}
            placeholder="target@example.com"
            className="flex-1 bg-background border border-panel-border text-foreground rounded px-4 py-3 font-mono focus:outline-none focus:border-accent transition-colors placeholder:text-gray-600 disabled:opacity-50"
          />
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting || pollStatus === "pending"}
          className="relative w-full bg-panel text-accent border border-accent rounded py-3 font-mono font-bold hover:bg-accent hover:text-background transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-[0.2em] overflow-hidden group"
        >
          <span className="absolute inset-0 w-full h-full bg-accent/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></span>
          <span className="relative z-10 flex items-center justify-center gap-2">
            {isSubmitting || pollStatus === "pending" ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                EXECUTING...
              </>
            ) : "INITIATE SCAN"}
          </span>
        </button>
      </form>

      {error && (
        <div className="w-full max-w-3xl bg-red-900/20 border border-red-500/50 text-red-400 p-4 rounded font-mono text-sm text-center">
          {error}
        </div>
      )}

      {renderResults()}
    </div>
  );
}
