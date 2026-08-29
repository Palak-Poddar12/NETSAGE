import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  LayoutDashboard,
  FolderGit2,
  PlusCircle,
  Activity,
  CheckSquare,
  Sun,
  Moon,
  Zap,
  Terminal,
  FileText,
  X,
} from 'lucide-react';
import { useCaseContext } from '../context/CaseContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from './Toast';

export function CommandPalette({ isOpen, setIsOpen }) {
  const navigate = useNavigate();
  const { cases } = useCaseContext();
  const { isDark, toggleTheme } = useTheme();
  const { addToast } = useToast();
  const [query, setQuery] = useState('');

  // Keyboard shortcut listener for Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setIsOpen]);

  if (!isOpen) return null;

  const quickActions = [
    {
      title: 'Open NOC Dashboard',
      icon: LayoutDashboard,
      shortcut: 'G D',
      action: () => navigate('/dashboard'),
    },
    {
      title: 'Create New Case',
      icon: PlusCircle,
      shortcut: 'G N',
      action: () => navigate('/new-case'),
    },
    {
      title: 'View Case Ledger',
      icon: FolderGit2,
      shortcut: 'G C',
      action: () => navigate('/cases'),
    },
    {
      title: isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode',
      icon: isDark ? Sun : Moon,
      shortcut: 'T T',
      action: () => toggleTheme(),
    },
  ];

  // Filter cases based on search query
  const filteredCases = cases.filter(
    (c) =>
      c.case_id.toLowerCase().includes(query.toLowerCase()) ||
      c.symptom.toLowerCase().includes(query.toLowerCase()) ||
      c.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelectCase = (c) => {
    setIsOpen(false);
    navigate(`/diagnosis/${c.diagnosis_id || `DIAG-${c.case_id}`}`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="w-full max-w-xl bg-white dark:bg-[#0c1829] rounded-2xl border border-slate-200 dark:border-[#1e3450] shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header */}
        <div className="flex items-center px-4 border-b border-slate-200 dark:border-[#1e3450] bg-slate-50/70 dark:bg-[#07101c]">
          <Search className="w-4 h-4 text-slate-400 mr-3" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or search incidents (e.g. CASE-001, VLAN, OSPF)..."
            className="w-full py-3.5 bg-transparent text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none font-sans"
          />
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white rounded-lg"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 divide-y divide-slate-100 dark:divide-[#152538] text-xs">
          {/* Quick Actions */}
          {!query && (
            <div className="py-2">
              <div className="px-3 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                Quick Commands
              </div>
              {quickActions.map((action, idx) => {
                const Icon = action.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => {
                      action.action();
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-100 dark:hover:bg-[#102035] text-slate-700 dark:text-slate-200 transition-colors"
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4 text-sky-600 dark:text-sky-400" />
                      <span className="font-medium">{action.title}</span>
                    </div>
                    <kbd className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-[#08111c] text-slate-500 border border-slate-200 dark:border-[#1e3450]">
                      {action.shortcut}
                    </kbd>
                  </button>
                );
              })}
            </div>
          )}

          {/* Incidents Search Results */}
          <div className="py-2">
            <div className="px-3 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 font-mono">
              Cisco Telemetry Incidents ({filteredCases.length})
            </div>
            {filteredCases.length === 0 ? (
              <div className="p-4 text-center text-slate-400 text-xs font-mono">
                No incidents match "{query}"
              </div>
            ) : (
              filteredCases.map((c) => (
                <button
                  key={c.case_id}
                  onClick={() => handleSelectCase(c)}
                  className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-100 dark:hover:bg-[#102035] transition-colors flex items-center justify-between group"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-sky-600 dark:text-sky-400">
                        {c.case_id}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-[#08111c] text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-[#1e3450]">
                        {c.category}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 dark:text-slate-300 line-clamp-1">
                      {c.symptom}
                    </p>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    Diagnose &rarr;
                  </span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Footer info */}
        <div className="px-4 py-2 bg-slate-50 dark:bg-[#07101c] border-t border-slate-200 dark:border-[#1e3450] flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>Navigate with arrows • Press ESC to exit</span>
          <span className="text-sky-600 dark:text-sky-400">NetSage Command Engine</span>
        </div>
      </div>
    </div>
  );
}

export default CommandPalette;
