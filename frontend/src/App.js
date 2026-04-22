import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { Toaster } from "sonner";
import Landing from "@/pages/Landing";
import Login from "@/pages/Login";
import AppShell from "@/components/AppShell";
import SuperAdminDashboard from "@/pages/SuperAdminDashboard";
import ClientDashboard from "@/pages/ClientDashboard";
import Assets from "@/pages/Assets";
import AssetDetail from "@/pages/AssetDetail";
import Inspections from "@/pages/Inspections";
import Maintenance from "@/pages/Maintenance";
import Incidents from "@/pages/Incidents";
import Wallet from "@/pages/Wallet";
import Documents from "@/pages/Documents";
import NotificationsPage from "@/pages/NotificationsPage";
import Sites from "@/pages/Sites";
import Users from "@/pages/Users";
import Support from "@/pages/Support";
import HelpCenter from "@/pages/HelpCenter";
import Terms from "@/pages/Terms";
import ClientsAdmin from "@/pages/ClientsAdmin";
import ComplianceCenter from "@/pages/ComplianceCenter";
import RiskMap from "@/pages/RiskMap";
import "@/index.css";

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen grid place-items-center text-xs mono">INITIALIZING SYSTEM…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function RoleHome() {
  const { user } = useAuth();
  if (user?.role === "super_admin") return <Navigate to="/app/sspl" replace />;
  return <Navigate to="/app/dashboard" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <Toaster position="top-right" richColors />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/app" element={<Protected><AppShell /></Protected>}>
            <Route index element={<RoleHome />} />
            <Route path="sspl" element={<SuperAdminDashboard />} />
            <Route path="clients" element={<ClientsAdmin />} />
            <Route path="dashboard" element={<ClientDashboard />} />
            <Route path="assets" element={<Assets />} />
            <Route path="assets/:id" element={<AssetDetail />} />
            <Route path="inspections" element={<Inspections />} />
            <Route path="maintenance" element={<Maintenance />} />
            <Route path="incidents" element={<Incidents />} />
            <Route path="compliance" element={<ComplianceCenter />} />
            <Route path="risk-map" element={<RiskMap />} />
            <Route path="wallet" element={<Wallet />} />
            <Route path="documents" element={<Documents />} />
            <Route path="sites" element={<Sites />} />
            <Route path="users" element={<Users />} />
            <Route path="support" element={<Support />} />
            <Route path="help" element={<HelpCenter />} />
            <Route path="notifications" element={<NotificationsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
