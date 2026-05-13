import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignApi } from "../lib/api";
import { Plus, Trash2, FolderOpen } from "lucide-react";

export default function CampaignsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", target: "" });

  const { data: campaigns = [] } = useQuery({ queryKey: ["campaigns"], queryFn: campaignApi.list });
  const safeCampaigns = Array.isArray(campaigns) ? campaigns : [];

  const createMutation = useMutation({
    mutationFn: () => campaignApi.create(form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["campaigns"] }); setShowForm(false); setForm({ name: "", description: "", target: "" }); },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => campaignApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["campaigns"] }),
  });

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-white">Campaigns</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
        >
          <Plus size={16} /> New Campaign
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-6">
          <h2 className="text-sm font-medium text-gray-300 mb-4">Create Campaign</h2>
          <div className="space-y-3">
            <input className={inp} placeholder="Campaign name *" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            <input className={inp} placeholder="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
            <input className={inp} placeholder="Target org / domain (e.g. target.com)" value={form.target} onChange={e => setForm(f => ({ ...f, target: e.target.value }))} />
            <div className="flex gap-3">
              <button onClick={() => createMutation.mutate()} disabled={!form.name || createMutation.isPending}
                className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 disabled:opacity-50 transition-colors">
                Create
              </button>
              <button onClick={() => setShowForm(false)} className="text-gray-500 text-sm px-4 py-2 hover:text-gray-200">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {safeCampaigns.length === 0 ? (
        <div className="text-center py-20 text-gray-600">
          <FolderOpen size={36} className="mx-auto mb-3 opacity-30" />
          <p>No campaigns yet.</p>
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl border border-gray-800 divide-y divide-gray-800">
          {safeCampaigns.map(c => (
            <div key={c.id} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium text-gray-200">{c.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{c.target && `Target: ${c.target} · `}{c.email_count} emails</p>
              </div>
              <button onClick={() => deleteMutation.mutate(c.id)} className="text-gray-700 hover:text-red-400 transition-colors">
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const inp = "w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 placeholder-gray-600";
