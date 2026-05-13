import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { emailApi } from "../lib/api";
import { ChevronRight, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { clsx } from "clsx";

function ThreatBadge({ score }: { score?: number }) {
  if (score == null) return <span className="text-gray-600 text-xs">—</span>;
  const color = score >= 60 ? "text-red-400" : score >= 30 ? "text-yellow-400" : "text-green-400";
  return <span className={clsx("text-xs font-mono font-semibold", color)}>{score}</span>;
}

function AuthBadge({ result }: { result?: string }) {
  if (!result) return <span className="text-gray-700 text-xs">—</span>;
  if (result === "pass") return <CheckCircle size={13} className="text-green-500" />;
  return <XCircle size={13} className="text-red-500" />;
}

export default function EmailsPage() {
  const [minScore, setMinScore] = useState<number | undefined>();

  const { data: emails = [], isLoading } = useQuery({
    queryKey: ["emails", minScore],
    queryFn: () => emailApi.list({ min_threat_score: minScore, limit: 100 }),
  });

  const safeEmails = Array.isArray(emails) ? emails : [];

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-white">Emails</h1>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-400">Min threat score:</label>
          <select
            className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-1.5"
            value={minScore ?? ""}
            onChange={e => setMinScore(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">All</option>
            <option value="30">30+</option>
            <option value="60">60+</option>
            <option value="80">80+</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <p className="text-gray-500 text-sm">Loading…</p>
      ) : safeEmails.length === 0 ? (
        <div className="text-center py-20 text-gray-600">
          <AlertTriangle size={36} className="mx-auto mb-3 opacity-30" />
          <p>No emails ingested yet.</p>
          <Link to="/ingest" className="text-red-400 text-sm mt-2 inline-block hover:underline">Ingest your first email →</Link>
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase">
                <th className="text-left px-4 py-3">Sender</th>
                <th className="text-left px-4 py-3">Subject</th>
                <th className="text-left px-4 py-3">SPF</th>
                <th className="text-left px-4 py-3">DKIM</th>
                <th className="text-left px-4 py-3">DMARC</th>
                <th className="text-left px-4 py-3">Score</th>
                <th className="text-left px-4 py-3">Received</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {safeEmails.map(e => (
                <tr key={e.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-3 text-gray-300 truncate max-w-[160px]">{e.sender || "—"}</td>
                  <td className="px-4 py-3 text-gray-300 truncate max-w-[200px]">{e.subject || "(no subject)"}</td>
                  <td className="px-4 py-3"><AuthBadge result={e.spf_result} /></td>
                  <td className="px-4 py-3"><AuthBadge result={e.dkim_result} /></td>
                  <td className="px-4 py-3"><AuthBadge result={e.dmarc_result} /></td>
                  <td className="px-4 py-3"><ThreatBadge score={e.threat_score} /></td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{new Date(e.received_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <Link to={`/emails/${e.id}`} className="text-gray-600 hover:text-red-400 transition-colors">
                      <ChevronRight size={16} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
