"use client";

import { useEffect, useState, useMemo } from "react";
import dynamic from "next/dynamic";
import { searchApi } from "@/services/api";

// react-force-graph accesses window directly, so we must load it dynamically with ssr disabled
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

export default function GraphPage() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Custom colors based on node labels
  const getNodeColor = (node: any) => {
    switch(node.label) {
      case "Domain": return "#00ff9d"; // Accent neon green
      case "Email": return "#3b82f6"; // Blue
      case "GitHubUser": return "#a855f7"; // Purple
      case "IPAddress": return "#f59e0b"; // Orange
      default: return "#eaeaea";
    }
  };

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const data = await searchApi.getGraph();
        setGraphData(data);
      } catch (err: any) {
        setError(err.message || "Failed to load graph data");
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, []);

  return (
    <div className="w-full h-full flex flex-col gap-4 animate-fade-in relative">
      <div className="absolute top-0 left-0 z-10 p-4 pointer-events-none">
        <h2 className="text-3xl font-mono font-bold tracking-tight text-foreground">
          INTELLIGENCE <span className="text-accent glow-text">GRAPH</span>
        </h2>
        <p className="text-gray-400 font-mono text-sm mt-1">
          Visualizing relationships across all stored targets.
        </p>
        
        {/* Legend */}
        <div className="mt-4 flex flex-col gap-2 font-mono text-xs">
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#00ff9d]"></span> Domain</div>
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#3b82f6]"></span> Email</div>
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#a855f7]"></span> User (GitHub)</div>
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#f59e0b]"></span> IP Address</div>
        </div>
      </div>

      {error && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 bg-red-900/80 border border-red-500/50 text-red-400 p-4 rounded font-mono text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="w-full h-[600px] flex items-center justify-center">
          <div className="w-16 h-16 border-4 border-panel-border border-t-accent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="w-full h-[700px] bg-panel border border-panel-border rounded-lg overflow-hidden glow-box cursor-crosshair">
          <ForceGraph2D
            graphData={graphData}
            nodeLabel="value"
            nodeColor={getNodeColor}
            nodeRelSize={6}
            linkColor={() => "rgba(0, 255, 157, 0.2)"} // Muted accent for links
            linkWidth={1.5}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
            linkDirectionalParticleColor={() => "#00ff9d"}
            backgroundColor="#050505" // Match our background
            onNodeClick={(node) => {
              // Can integrate click handlers to show panel with node details
              console.log(node);
            }}
          />
        </div>
      )}
    </div>
  );
}
