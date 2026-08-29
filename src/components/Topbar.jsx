import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Menu,
  Plus,
  RefreshCw,
  Activity,
  ChevronDown,
  Sun,
  Moon,
  Search,
} from 'lucide-react';
import { useHealth } from '../hooks/useApi';
import { useCaseContext } from '../context/CaseContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from './Toast';
import { CommandPalette } from './CommandPalette';

export function Topbar({ onMenuClick }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { status, checkNow } = useHealth(15000);
  const { cases } = useCaseContext();
  const { theme, toggleTheme, isDark } = useTheme();
  const { addToast } = useToast();
  const [caseDropdownOpen, setCaseDropdownOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  const getPageTitle = () => {
    const path = location.pathname;
    if (path.startsWith('/dashboard')) return { title: 'Network Operations Center', tag: 'NOC-MONITOR' };
    if (path.startsWith('/cases')) return { title: 'Troubleshooting Incidents', tag: 'CASE-LEDGER' };
    if (path.startsWith('/new-case')) return { title: 'Ingest Network Incident', tag: 'TAC-SUBMIT' };
    if (path.startsWith('/diagnosis')) return { title: 'AI & Rule Diagnostic Lab', tag: 'DIAGNOSTICS' };
    if (path.startsWith('/review')) return { title: 'Human Review & Verification', tag: 'HITL-AUDIT' };
    return { title: 'NetSage AI Platform', tag: 'CISCO-TAC' };
  };

  const pageInfo = getPageTitle();

  const handleRefresh = async () => {
    await checkNow();
    addToast('Telemetry connection pinged successfully.', 'info');
  };

  return (
    <>
      <CommandPalette
        isOpen={commandPaletteOpen}
        setIsOpen={setCommandPaletteOpen}
      />

      <header className="h-16 bg-white dark:bg-[#0b1727] border-b border-slate-200 dark:border-[#1e3450] px-4 lg:px-8 flex items-center justify-between sticky top-0 z-30 shadow-subtle transition-colors duration-200">
        {/* Left section: Hamburger & Breadcrumb */}
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800 lg:hidden transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2.5">
            <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-sky-50 text-sky-700 dark:bg-sky-950/80 dark:text-sky-300 border border-sky-200 dark:border-sky-800/60 font-bold hidden sm:inline-block">
              {pageInfo.tag}
            </span>
            <h1 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white tracking-tight">
              {pageInfo.title}
            </h1>
          </div>
        </div>

        {/* Right section: Search bar / Palette trigger, Case Switcher, Theme Switcher, Health & Action */}
        <div className="flex items-center gap-2.5">
          {/* Global Quick Search Button (Ctrl+K) */}
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-[#08111c] border border-slate-200 dark:border-[#1e3450] text-xs text-slate-500 hover:text-slate-900 dark:hover:text-white hover:border-sky-400 transition-colors font-sans"
          >
            <Search className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden md:inline">Quick Search...</span>
            <kbd className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-white dark:bg-[#0c1829] text-slate-400 border border-slate-200 dark:border-[#1e3450]">
              Ctrl K
            </kbd>
          </button>

          {/* Switch Case Quick Selector */}
          <div className="relative hidden md:block">
            <button
              onClick={() => setCaseDropdownOpen(!caseDropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-[#08111c] border border-slate-200 dark:border-[#1e3450] text-xs font-mono text-slate-700 dark:text-slate-200 hover:border-sky-400 transition-colors"
            >
              <Activity className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
              <span>Switch Case</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {caseDropdownOpen && (
              <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-[#0b1727] rounded-2xl border border-slate-200 dark:border-[#1e3450] shadow-xl p-2 z-50 divide-y divide-slate-100 dark:divide-slate-800">
                <div className="px-2 py-1.5 text-[10px] font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 font-mono">
                  Recent Network Incidents
                </div>
                <div className="py-1 max-h-56 overflow-y-auto space-y-1">
                  {cases.slice(0, 6).map((c) => (
                    <button
                      key={c.case_id}
                      onClick={() => {
                        setCaseDropdownOpen(false);
                        navigate(`/diagnosis/${c.diagnosis_id || `DIAG-${c.case_id}`}`);
                      }}
                      className="w-full text-left p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-[#102035] text-xs transition-colors flex items-center justify-between"
                    >
                      <div>
                        <div className="font-mono font-bold text-sky-600 dark:text-sky-400">{c.case_id}</div>
                        <div className="text-[11px] text-slate-600 dark:text-slate-300 truncate max-w-[180px]">
                          {c.symptom}
                        </div>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">{c.category}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Theme Mode Toggle Button */}
          <button
            onClick={toggleTheme}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-[#08111c] dark:hover:bg-[#122438] text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-[#1e3450] transition-colors"
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          {/* Live Backend Connection Indicator */}
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-mono transition-colors ${
              status === 'connected'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-300'
                : 'bg-slate-100 dark:bg-[#08111c] border-slate-200 dark:border-[#1e3450] text-slate-600 dark:text-slate-300'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'connected' ? 'bg-emerald-500 animate-ping' : 'bg-sky-500'
              }`}
            />
            <span className="hidden sm:inline font-medium">
              {status === 'connected' ? 'Connected' : 'Demo Mode'}
            </span>
            <button
              onClick={handleRefresh}
              title="Refresh status"
              className="text-slate-400 hover:text-slate-700 dark:hover:text-white transition-transform active:rotate-180"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>

          {/* Quick New Case CTA */}
          <Link
            to="/new-case"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-sm hover:shadow transition-all active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Create Case</span>
          </Link>
        </div>
      </header>
    </>
  );
}

export default Topbar;
