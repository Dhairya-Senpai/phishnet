import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { emailApi } from "../lib/api";
import { ArrowLeft, ExternalLink, AlertTriangle } from "lucide-react";
import { clsx } from "clsx";

export default function EmailDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: email, isLoading } = useQuery({
    queryKey: ["email", id],
    queryFn: () => emailApi.get(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="p-8 text-gray-500">Loading…</div>;
  if (!email)    return <div className="p-8 text-gray-500">Email not found.</div>;

  const score = email.threat_score ?? 0;
  const scoreColor = score >= 60 ? "text-red-400" : score >= 30 ? "text-yellow-400" : "text-green-400";

  return (
    <div className="p-8 max-w-5xl">
      <Link to="/emails" className="flex items-center gap-2 text-gray-500 hover:text-gray-200 text-sm mb-6 transition-colors">
        <ArrowLeft size={14} /> Back to Emails
      </Link>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-white">{email.subject || "(no subject)"}</h1>
          <p className="text-sm text-gray-500 mt-1">{email.sender} → {email.recipient}</p>
        </div>
        <div className="text-right">
          <p className={clsx("text-3xl font-mono font-bold", scoreColor)}>{score}</p>
          <p className="text-xs text-gray-600">threat score</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <AuthCard label="SPF"   result={email.spf_result}   domain={email.spf_result} />
        <AuthCard label="DKIM"  result={email.dkim_result}  domain={undefined} />
        <AuthCard label="DMARC" result={email.dmarc_result} domain={undefined} />
      </div>

      {/* Bypass indicators */}
      {email.bypass_indicators && email.bypass_indicators.length > 0 && (
        <div className="bg-red-950/30 border border-red-800/50 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={14} className="text-red-400" />
            <span className="text-sm font-medium text-red-400">Bypass Indicators</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {email.bypass_indicators.map((ind) => (
              <span key={ind} className="text-xs bg-red-900/50 text-red-300 px-2 py-1 rounded">{ind}</span>
            ))}
          </div>
        </div>
      )}

      {/* Relay path */}
      {email.relay_path && email.relay_path.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 mb-6">
          <h2 className="text-sm font-medium text-gray-400 mb-3">Relay Path</h2>
          <div className="space-y-2">
            {email.relay_path.map((hop, i) => (
              <div key={i} className="flex items-center gap-3 text-xs">
                <span className="text-gray-600 w-4">{i + 1}</span>
                {hop.ip && <span className="font-mono text-blue-400">{hop.ip}</span>}
                {hop.by && <span className="text-gray-400">→ {hop.by}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted links */}
      {email.links && email.links.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 mb-6">
          <h2 className="text-sm font-medium text-gray-400 mb-3">Extracted Links ({email.links.length})</h2>
          <div className="space-y-2">
            {email.links.map((link) => (
              <div key={link.id} className="flex items-center gap-3 text-xs">
                {link.is_redirect && (
                  <span className="bg-red-900/50 text-red-300 px-1.5 py-0.5 rounded text-[10px]">REDIRECT</span>
                )}
                <span className="text-gray-400 truncate flex-1">{link.url}</span>
                {link.anchor_text && <span className="text-gray-600 italic">"{link.anchor_text}"</span>}
                <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-blue-400">
                  <ExternalLink size={12} />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw headers */}
      <details className="bg-gray-900 rounded-xl border border-gray-800 p-4">
        <summary className="text-sm font-medium text-gray-400 cursor-pointer">Raw Headers</summary>
        <pre className="mt-3 text-xs text-gray-500 overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(email.raw_headers, null, 2)}
        </pre>
      </details>
    </div>
  );
}

function AuthCard({ label, result, domain }: { label: string; result?: string; domain?: string }) {
  const color = result === "pass" ? "border-green-800/50 bg-green-950/20"
    : result ? "border-red-800/50 bg-red-950/20"
    : "border-gray-800 bg-gray-900";
  const textColor = result === "pass" ? "text-green-400" : result ? "text-red-400" : "text-gray-600";

  return (
    <div className={clsx("rounded-xl border p-4", color)}>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={clsx("text-lg font-semibold uppercase", textColor)}>{result || "none"}</p>
      {domain && <p className="text-xs text-gray-600 mt-1">{domain}</p>}
    </div>
  );
}
