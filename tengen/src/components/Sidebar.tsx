// src/components/Sidebar.tsx
import { Home, BarChart, Settings } from "lucide-react";

export default function Sidebar() {
  return (
    <div className="h-screen w-60 bg-gray-900 text-white p-4 flex flex-col">
      <h1 className="text-2xl font-bold mb-8">Tengen.ai</h1>
      <nav className="flex flex-col gap-4">
        <a href="/" className="flex items-center gap-2 hover:text-gray-300"><Home /> Dashboard</a>
        <a href="/analytics" className="flex items-center gap-2 hover:text-gray-300"><BarChart /> Analytics</a>
        <a href="/settings" className="flex items-center gap-2 hover:text-gray-300"><Settings /> Settings</a>
      </nav>
    </div>
  );
}
