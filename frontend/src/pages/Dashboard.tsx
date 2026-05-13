import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "../lib/api";
import { Shield, Mail, FolderOpen, AlertTriangle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6"];

export default function DashboardPage() {
  const { data: stats } = useQuery({ queryKey: ["overview"], queryFn: analyticsApi.overview });
  const { data: threatDist = [] } = useQuery({ queryKey: ["threat-dist"], queryFn: () => analyticsApi.threatDistribution() });
  const { data: timeline = [] } = useQuery({ queryKey: ["auth-timeline"], queryFn: () => analyticsApi.authTimeline() });
  const { data: indicators = [] } = useQuery({ queryKey: ["bypass-indicators"], queryFn: analyticsApi.bypassIndicators });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold text-white mb-6">Dashboard</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={<Mail size={18} />}      label="Total Emails"    value={stats?.total_emails ?? 0}    color="blue" />
        <StatCard icon={<FolderOpen size={18} />} label="Campaigns"      value={stats?.total_campaigns ?? 0} color="purple" />
        <StatCard icon={<AlertTriangle size={18} />} label="High Threat" value={stats?.recent_bypass_count ?? 0} color="red" />
        <StatCard icon={<Shield size={18} />}    label="Avg Threat Score" value={stats?.avg_threat_score ?? 0} color="orange" suffix="/ 100" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Auth timeline */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h2 className="text-sm font-medium text-gray-400 mb-4">SPF Auth Results (30 days)</h2>
          {timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={timeline}>
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} />
                <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151" }} />
                <Bar dataKey="spf_pass" fill="#22c55e" name="Pass" radius={[2, 2, 0, 0]} />
                <Bar dataKey="spf_fail" fill="#ef4444" name="Fail" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState message="No timeline data yet" />
          )}
        </div>

        {/* Threat distribution */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h2 className="text-sm font-medium text-gray-400 mb-4">Threat Score Distribution</h2>
          {threatDist.some(d => d.count > 0) ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={threatDist} dataKey="count" nameKey="range" cx="50%" cy="50%" outerRadius={80} label={({ range }) => range}>
                  {threatDist.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState message="No threat data yet" />
          )}
        </div>
      </div>

      {/* Bypass indicators */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <h2 className="text-sm font-medium text-gray-400 mb-4">Top Bypass Indicators</h2>
        {indicators.length > 0 ? (
          <div className="space-y-2">
            {indicators.slice(0, 8).map((item) => (
              <div key={item.indicator} className="flex items-center gap-3">
                <div className="flex-1 text-sm text-gray-300">{item.indicator}</div>
                <div className="text-sm font-mono text-red-400">{item.count}</div>
                <div className="w-32 bg-gray-800 rounded-full h-1.5">
                  <div
                    className="bg-red-500 h-1.5 rounded-full"
                    style={{ width: `${Math.min((item.count / (indicators[0]?.count || 1)) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState message="No bypass indicators yet" />
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color, suffix = "" }: {
  icon: React.ReactNode; label: string; value: number; color: string; suffix?: string;
}) {
  const colors: Record<string, string> = {
    blue: "bg-blue-500/10 text-blue-400", purple: "bg-purple-500/10 text-purple-400",
    red: "bg-red-500/10 text-red-400", orange: "bg-orange-500/10 text-orange-400",
  };
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <div className={`inline-flex p-2 rounded-lg ${colors[color]} mb-3`}>{icon}</div>
      <p className="text-2xl font-semibold text-white">{typeof value === "number" ? value.toLocaleString() : value}{suffix}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p className="text-gray-600 text-sm text-center py-8">{message}</p>;
}
