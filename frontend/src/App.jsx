import React, { useState } from 'react';
import { 
  Shield, 
  LayoutDashboard, 
  FileSearch, 
  Network, 
  MapPin, 
  MessageSquareCode, 
  FileText, 
  AlertTriangle 
} from 'lucide-react';
import mockEvidence from './mockData/evidenceMock.json';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between">
        <div>
          {/* Logo Brand Title */}
          <div className="p-5 flex items-center gap-3 border-b border-slate-800">
            <Shield className="w-8 h-8 text-emerald-500 animate-pulse" />
            <div>
              <h1 className="font-bold text-md tracking-wide">SENTINEL SHIELD</h1>
              <span className="text-xs text-slate-500 font-semibold">AI SAFETY PORTAL</span>
            </div>
          </div>

          {/* Navigation Options */}
          <nav className="p-4 space-y-2">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'analyzer', label: 'File Analyzer', icon: FileSearch },
              { id: 'graph', label: 'Fraud Graph', icon: Network },
              { id: 'heatmap', label: 'Crime Hotspots', icon: MapPin },
              { id: 'copilot', label: 'Investigation Copilot', icon: MessageSquareCode },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === item.id 
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30' 
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* System User Footer badge */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/50 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold text-sm">
            NJ
          </div>
          <div>
            <p className="text-xs font-semibold">Nikhil Jha</p>
            <p className="text-[10px] text-slate-500">Investigator ID: #8131</p>
          </div>
        </div>
      </aside>

      {/* RIGHT CONTENT WORKSPACE */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* Top Floating Control Bar */}
        <header className="h-16 border-b border-slate-800 bg-slate-950/30 backdrop-blur-md flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <span className="text-xs font-mono bg-slate-800 px-3 py-1.5 rounded-md border border-slate-700 text-slate-300">
              Active Session: {mockEvidence.case_id}
            </span>
            <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              Agent Core Live
            </span>
          </div>
          <div className="text-sm font-medium text-slate-400">
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
        </header>

        {/* VIEW WORKSPACE ROUTER ROUTING PARALLEL */}
        <div className="p-8 flex-1">
          {activeTab === 'dashboard' && (
            <div className="space-y-6 animate-fadeIn">
              <h2 className="text-2xl font-bold tracking-tight">Overview Dashboard</h2>
              <p className="text-slate-400 text-sm">Welcome back, Investigator. Here is the operational intelligence overview matrix.</p>
              
              {/* Rapid Metrics Cards grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex items-start justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">Current Case Risk</p>
                    <p className="text-3xl font-extrabold mt-2 text-rose-500">{(mockEvidence.overall_risk_score * 100)}%</p>
                  </div>
                  <span className="p-2 bg-rose-500/10 text-rose-400 rounded-xl"><AlertTriangle className="w-6 h-6"/></span>
                </div>

                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex items-start justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">Risk Category</p>
                    <p className="text-3xl font-extrabold mt-2 text-amber-500">{mockEvidence.risk_category}</p>
                  </div>
                  <span className="p-2 bg-amber-500/10 text-amber-400 rounded-xl"><Shield className="w-6 h-6"/></span>
                </div>

                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex items-start justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">Linked IPC Sections</p>
                    <p className="text-3xl font-extrabold mt-2 text-emerald-400">{mockEvidence.ipc_sections.length}</p>
                  </div>
                  <span className="p-2 bg-emerald-500/10 text-emerald-400 rounded-xl"><FileText className="w-6 h-6"/></span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analyzer' && <div className="text-slate-400 text-sm">File Analyzer Panel (Will integrate Drag-&-Drop workspace next)</div>}
          {activeTab === 'graph' && <div className="text-slate-400 text-sm">Fraud Graph Intelligence Network View</div>}
          {activeTab === 'heatmap' && <div className="text-slate-400 text-sm">Geospatial Regional Hotspots Heatmap Layout</div>}
          {activeTab === 'copilot' && <div className="text-slate-400 text-sm">Investigation Copilot AI Agent Chat Interface</div>}
        </div>
      </main>
    </div>
  );
}