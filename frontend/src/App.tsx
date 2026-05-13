import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/dashboard/Layout";
import DashboardPage from "./pages/Dashboard";
import EmailsPage from "./pages/Emails";
import EmailDetailPage from "./pages/EmailDetail";
import CampaignsPage from "./pages/Campaigns";
import IngestPage from "./pages/Ingest";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"  element={<DashboardPage />} />
          <Route path="emails"     element={<EmailsPage />} />
          <Route path="emails/:id" element={<EmailDetailPage />} />
          <Route path="campaigns"  element={<CampaignsPage />} />
          <Route path="ingest"     element={<IngestPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
