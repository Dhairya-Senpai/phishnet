import { Outlet, NavLink } from "react-router-dom";
import { LayoutDashboard, Mail, FolderOpen, Upload, Shield } from "lucide-react";
import { clsx } from "clsx";

const nav = [
  { to: "/dashboard", label: "Dashboard",  icon: LayoutDashboard },
  { to: "/emails",    label: "Emails",     icon: Mail },
  { to: "/campaigns", label: "Campaigns",  icon: FolderOpen },
  { to: "/ingest",    label: "Ingest",     icon: Upload },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-gray-800">
          <div className="bg-red-600 text-white rounded-lg p-1.5">
            <Shield size={16} />
          </div>
          <span className="font-semibold text-white text-lg tracking-tight">Phishnet</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-red-600/20 text-red-400"
                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
                )
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-gray-800">
          <p className="text-xs text-gray-600">Phishnet v0.1.0</p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto bg-gray-950">
        <Outlet />
      </main>
    </div>
  );
}
