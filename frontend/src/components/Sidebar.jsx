import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderGit2,
  PlusCircle,
  Activity,
  CheckSquare,
  Radio,
  Server,
  Zap,
  Network,
  Shield,
  Layers,
  GraduationCap,
  Award,
} from 'lucide-react';
import { CiscoLogo } from './CiscoLogo';
import { useHealth } from '../hooks/useApi';
import { useCaseContext } from '../context/CaseContext';

export function Sidebar({ isOpen, setIsOpen }) {
  const { status } = useHealth(15000);
  const { cases } = useCaseContext();

  const navItems = [
    { name: 'NetAcad Dashboard', path: '/dashboard', icon: LayoutDashboard, badge: 'Live' },
    { name: 'Incident Lab Ledger', path: '/cases', icon: FolderGit2, count: cases.length },
    { name: 'Ingest Incident', path: '/new-case', icon: PlusCircle, highlight: true },
    { name: 'Diagnostic Lab', path: '/diagnosis/DIAG-CASE-001', icon: Activity },
    { name: 'Engineer Review Audit', path: '/review/DIAG-CASE-001', icon: CheckSquare },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-white dark:bg-[#0b1727] border-r border-slate-200 dark:border-[#1e3450] flex flex-col transition-colors duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-20 px-5 flex items-center border-b border-slate-200 dark:border-[#1e3450] bg-slate-50/80 dark:bg-[#07101c]">
          <CiscoLogo />
        </div>

        {/* Navigation Section */}
        <div className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 font-mono flex items-center gap-1.5">
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Lab Curriculum & Operations</span>
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-sky-50 dark:bg-[#132840] text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-500/40 font-bold shadow-sm'
                      : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-[#102035] border border-transparent'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
                    {item.badge}
                  </span>
                )}
                {item.count !== undefined && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 dark:bg-[#08111c] text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-[#1e3450]">
                    {item.count}
                  </span>
                )}
              </NavLink>
            );
          })}

          {/* Cisco NetAcad Certification Modules */}
          <div className="pt-6 px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 font-mono flex items-center gap-1.5">
            <Award className="w-3.5 h-3.5" />
            <span>Curriculum Tracks</span>
          </div>

          <div className="px-2 space-y-1.5">
            <div className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#08111c] border border-slate-200 dark:border-[#1e3450] text-xs flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
                <Layers className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
                <span className="font-medium">CCNA Switching / VLAN</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold">Active</span>
            </div>

            <div className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#08111c] border border-slate-200 dark:border-[#1e3450] text-xs flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
                <Network className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
                <span className="font-medium">CCNA OSPF / Routing</span>
              </div>
              <span className="text-[10px] font-mono text-sky-600 dark:text-sky-400 font-bold">Ready</span>
            </div>

            <div className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#08111c] border border-slate-200 dark:border-[#1e3450] text-xs flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
                <Shield className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                <span className="font-medium">CCNA Security / ACL</span>
              </div>
              <span className="text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold">Audit</span>
            </div>
          </div>
        </div>

        {/* System Status Footer */}
        <div className="p-3.5 border-t border-slate-200 dark:border-[#1e3450] bg-slate-50/80 dark:bg-[#07101c]">
          <div className="bg-white dark:bg-[#0a1626] rounded-xl p-3.5 border border-slate-200 dark:border-[#1e3450] shadow-sm space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">NetAcad Lab Node</span>
              </div>
              <span
                className={`inline-flex items-center gap-1.5 font-mono text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  status === 'connected'
                    ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60'
                    : 'bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800/60'
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    status === 'connected' ? 'bg-emerald-500 animate-ping' : 'bg-sky-500'
                  }`}
                />
                {status === 'connected' ? 'ONLINE' : 'LAB READY'}
              </span>
            </div>

            <div className="flex items-center justify-between text-[10px] text-slate-500 dark:text-slate-400 font-mono pt-1 border-t border-slate-100 dark:border-[#16273c]">
              <span>Rule Engine</span>
              <span className="text-sky-600 dark:text-sky-400 font-bold">v4.2-NetAcad</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
