import { useState, useEffect } from "react";
import { searchApi } from "@/services/api";
import { SearchResult } from "@/types";

export function useTaskPolling(taskId: string | null) {
  const [status, setStatus] = useState<string>("idle");
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) {
      setStatus("idle");
      setResults(null);
      setError(null);
      return;
    }

    let isSubscribed = true;
    setStatus("pending");

    const poll = async () => {
      try {
        const response = await searchApi.checkStatus(taskId);
        
        if (!isSubscribed) return;

        if (response.status === "completed" || response.status === "error" || response.status === "SUCCESS") {
          setStatus("completed");
          setResults(response.results || []);
        } else {
          // Continue polling if pending/running
          setTimeout(poll, 2000);
        }
      } catch (err: any) {
        if (!isSubscribed) return;
        setError(err.message || "Error polling task status");
        setStatus("error");
      }
    };

    poll();

    return () => {
      isSubscribed = false;
    };
  }, [taskId]);

  return { status, results, error };
}
