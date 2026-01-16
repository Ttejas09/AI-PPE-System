import { useState } from 'react';
import { Activity, Radio, TrendingUp } from 'lucide-react';
import AISystemStats from './pages/AISystemStats';
import LiveCommandCenter from './pages/LiveCommandCenter';
import HistoricalAnalysis from './pages/HistoricalAnalysis';

function App() {
  const [currentPage, setCurrentPage] = useState('stats');

  const navItems = [
    { id: 'stats', label: 'AI System Stats', icon: Activity },
    { id: 'live', label: 'Live Command Center', icon: Radio },
    { id: 'history', label: '30-Day Analysis', icon: TrendingUp },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'stats':
        return <AISystemStats />;
      case 'live':
        return <LiveCommandCenter />;
      case 'history':
        return <HistoricalAnalysis />;
      default:
        return <AISystemStats />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100 flex">
      <aside className="w-64 bg-gradient-to-b from-slate-900 to-slate-950 border-r border-cyan-500/20 flex flex-col">
        <div className="p-6 border-b border-cyan-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-red-500 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-red-400 bg-clip-text text-transparent">
                AI Safety
              </h1>
              <p className="text-xs text-gray-500">Monitoring System</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-red-500/20 border border-cyan-500/50 shadow-lg shadow-cyan-500/20'
                    : 'hover:bg-slate-800/50 border border-transparent hover:border-cyan-500/30'
                }`}
              >
                <Icon
                  className={`w-5 h-5 ${
                    isActive ? 'text-cyan-400' : 'text-gray-400'
                  }`}
                />
                <span
                  className={`text-sm font-medium ${
                    isActive ? 'text-cyan-400' : 'text-gray-400'
                  }`}
                >
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-cyan-500/20">
          <div className="bg-slate-800/50 rounded-lg p-3 border border-cyan-500/20">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-400">System Online</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
