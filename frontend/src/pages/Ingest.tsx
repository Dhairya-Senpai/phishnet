import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { emailApi, campaignApi } from "../lib/api";
import { Upload, CheckCircle } from "lucide-react";

const SAMPLE = `From: attacker@evil-domain.com
To: victim@company.com
Subject: Urgent: Verify your account
Message-ID: <abc123@evil-domain.com>
Authentication-Results: mx.company.com;
    spf=fail smtp.mailfrom=evil-domain.com;
    dkim=fail header.i=@evil-domain.com;
    dmarc=fail header.from=evil-domain.com
Received: from unknown ([192.168.1.100]) by mx.company.com

<html><body>
<p>Your account will be suspended. <a href="https://bit.ly/fake-login">Click here to verify</a></p>
<p>Visit <a href="https://tinyurl.com/reset-now">this link</a> immediately.</p>
</body></html>`;

export default function IngestPage() {
  const qc = useQueryClient();
  const [rawEmail, setRawEmail] = useState("");
  const [campaignId, setCampaignId] = useState("");
  const [lastResult, setLastResult] = useState<any>(null);

  const { data: campaigns = [] } = useQuery({ queryKey: ["campaigns"], queryFn: campaignApi.list });
  const safeCampaigns = Array.isArray(campaigns) ? campaigns : [];

  const ingestMutation = useMutation({
    mutationFn: () => emailApi.ingest(rawEmail, campaignId || undefined),
    onSuccess: (data) => {
      setLastResult(data);
      setRawEmail("");
      qc.invalidateQueries({ queryKey: ["emails"] });
      qc.invalidateQueries({ queryKey: ["overview"] });
    },
  });

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-semibold text-white mb-2">Ingest Email</h1>
      <p className="text-sm text-gray-500 mb-6">Paste a raw RFC 2822 email for analysis. Headers + body required.</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1.5">Campaign (optional)</label>
          <select className={sel} value={campaignId} onChange={e => setCampaignId(e.target.value)}>
            <option value="">None</option>
            {safeCampaigns.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-sm font-medium text-gray-400">Raw Email</label>
            <button onClick={() => setRawEmail(SAMPLE)} className="text-xs text-red-400 hover:text-red-300">
              Load sample phishing email
            </button>
          </div>
          <textarea
            className="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs font-mono rounded-lg px-3 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 placeholder-gray-700 resize-none"
            rows={16}
            placeholder="Paste raw email here (From: ... headers + body)…"
            value={rawEmail}
            onChange={e => setRawEmail(e.target.value)}
          />
        </div>

        <button
          onClick={() => ingestMutation.mutate()}
          disabled={!rawEmail.trim() || ingestMutation.isPending}
          className="flex items-center gap-2 bg-red-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50 transition-colors"
        >
          <Upload size={15} />
          {ingestMutation.isPending ? "Analyzing…" : "Ingest & Analyze"}
        </button>
      </div>

      {lastResult && (
        <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={16} className="text-green-400" />
            <span className="text-sm font-medium text-green-400">Analysis complete</span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-gray-500">Threat Score:</span> <span className="font-mono text-white ml-2">{lastResult.threat_score ?? "—"}</span></div>
            <div><span className="text-gray-500">SPF:</span> <span className="ml-2 text-white">{lastResult.spf_result || "—"}</span></div>
            <div><span className="text-gray-500">DKIM:</span> <span className="ml-2 text-white">{lastResult.dkim_result || "—"}</span></div>
            <div><span className="text-gray-500">DMARC:</span> <span className="ml-2 text-white">{lastResult.dmarc_result || "—"}</span></div>
          </div>
          {lastResult.bypass_indicators?.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-1">Indicators:</p>
              <div className="flex flex-wrap gap-1">
                {lastResult.bypass_indicators.map((i: string) => (
                  <span key={i} className="text-xs bg-red-900/40 text-red-300 px-2 py-0.5 rounded">{i}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const sel = "w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500";
