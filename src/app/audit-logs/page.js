"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${api.auditLogs}?limit=200`);
      const data = await response.json();

      if (data.success) {
        setLogs(data.logs || []);
      } else {
        setError(data.error || "Failed to fetch audit logs");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#141827] to-[#0f1525] text-[#e8eaf6]">
      <Navbar 
        pageTitle="Audit Logs"
        pageSubtitle="System activity history"
      />

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="rounded-xl bg-[#141827]/60 border border-red-900/20 p-6 shadow-xl shadow-black/30 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white">System Activity Log</h2>
            <button
              onClick={fetchLogs}
              className="px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-sm font-medium"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="h-8 w-8 animate-spin rounded-full border-3 border-red-400 border-t-transparent" />
            </div>
          ) : error ? (
            <div className="py-12 text-center">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-sm text-gray-400">No audit logs found.</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {logs.map((log) => (
                <div
                  key={log.table_id}
                  className="rounded-lg bg-[#0a0e1a]/50 border border-red-900/20 px-4 py-3 transition hover:bg-red-500/10 hover:border-red-500/30"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-sm text-white mb-1">{log.changes_to_data}</p>
                      <p className="text-xs text-gray-400">{formatDate(log.date)}</p>
                    </div>
                    <span className="text-xs text-gray-500">ID: {log.table_id}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {logs.length > 0 && (
            <div className="mt-4 text-center">
              <p className="text-xs text-gray-400">
                Showing {logs.length} log{logs.length !== 1 ? 's' : ''}
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

