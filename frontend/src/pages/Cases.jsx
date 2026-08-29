import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Filter,
  Layers,
  ArrowRight,
  Plus,
  RefreshCw,
  LayoutGrid,
  Table as TableIcon,
  FolderGit2,
} from 'lucide-react';
import { SeverityBadge } from '../components/SeverityBadge';
import { CaseCard } from '../components/CaseCard';
import { EmptyState } from '../components/EmptyState';
import { formatDate } from '../utils/formatters';
import { CATEGORIES, SEVERITIES } from '../utils/constants';
import { useCaseContext } from '../context/CaseContext';
import { useToast } from '../components/Toast';

export function Cases() {
  const { cases } = useCaseContext();
  const { addToast } = useToast();

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [viewMode, setViewMode] = useState('table'); // 'table' | 'cards'

  // Filtered Results
  const filteredCases = useMemo(() => {
    if (!Array.isArray(cases)) return [];
    return cases.filter((c) => {
      const matchesSearch =
        !searchTerm ||
        c.case_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.symptom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.concept?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCategory =
        selectedCategory === 'ALL' || c.category === selectedCategory;

      const matchesSeverity =
        selectedSeverity === 'ALL' || c.severity === selectedSeverity;

      const matchesStatus =
        selectedStatus === 'ALL' || c.status === selectedStatus;

      return matchesSearch && matchesCategory && matchesSeverity && matchesStatus;
    });
  }, [cases, searchTerm, selectedCategory, selectedSeverity, selectedStatus]);

  const handleRefresh = () => {
    addToast('Case repository synchronized with telemetry feed.', 'info');
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
            Network Troubleshooting Cases
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Central repository of Cisco telemetry, fault symptoms, and diagnostic evaluations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center bg-white dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <button
              onClick={() => setViewMode('table')}
              className={`p-1.5 rounded-lg transition-colors ${
                viewMode === 'table'
                  ? 'bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300'
                  : 'text-slate-400 hover:text-slate-700 dark:hover:text-white'
              }`}
              title="Table View"
            >
              <TableIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('cards')}
              className={`p-1.5 rounded-lg transition-colors ${
                viewMode === 'cards'
                  ? 'bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300'
                  : 'text-slate-400 hover:text-slate-700 dark:hover:text-white'
              }`}
              title="Card Grid View"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={handleRefresh}
            className="p-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white shadow-sm transition-colors"
            title="Refresh case repository"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <Link
            to="/new-case"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-sm hover:shadow transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Create Case</span>
          </Link>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white dark:bg-[#0d1524] p-4 rounded-2xl border border-slate-200 dark:border-slate-800 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 shadow-card">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search ID, symptom, keyword..."
            className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-colors"
          />
        </div>

        {/* Category Filter */}
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-sky-500 transition-colors"
        >
          <option value="ALL">All Categories</option>
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {/* Severity Filter */}
        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-sky-500 transition-colors"
        >
          <option value="ALL">All Severities</option>
          {SEVERITIES.map((sev) => (
            <option key={sev} value={sev}>
              {sev}
            </option>
          ))}
        </select>

        {/* Status Filter */}
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-sky-500 transition-colors"
        >
          <option value="ALL">All Statuses</option>
          <option value="REVIEWED">Reviewed</option>
          <option value="PENDING_REVIEW">Pending Review</option>
        </select>
      </div>

      {/* Main Content Area */}
      {filteredCases.length === 0 ? (
        <EmptyState
          title="No cases match your filters"
          description="Try clearing your search query or changing category and severity filters."
          icon={FolderGit2}
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchTerm('');
            setSelectedCategory('ALL');
            setSelectedSeverity('ALL');
            setSelectedStatus('ALL');
          }}
        />
      ) : viewMode === 'cards' ? (
        /* Card Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCases.map((caseItem) => (
            <CaseCard key={caseItem.case_id} caseItem={caseItem} />
          ))}
        </div>
      ) : (
        /* Enterprise Table View */
        <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-card">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/60 text-[11px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  <th className="py-3.5 px-4">Case ID</th>
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4 min-w-[240px]">Symptom</th>
                  <th className="py-3.5 px-4">Severity</th>
                  <th className="py-3.5 px-4">OSI Layer</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Created</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 text-xs">
                {filteredCases.map((c) => (
                  <tr
                    key={c.case_id}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-sky-600 dark:text-sky-400">
                      {c.case_id}
                    </td>
                    <td className="py-3.5 px-4 text-slate-800 dark:text-slate-300 font-medium">
                      {c.category}
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 dark:text-slate-200 line-clamp-1 max-w-md">
                      {c.symptom}
                    </td>
                    <td className="py-3.5 px-4">
                      <SeverityBadge severity={c.severity} />
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                      {c.osi_layer || 'Layer 3'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                          c.status === 'REVIEWED'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/70 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/40'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950/70 dark:text-amber-300 border-amber-200 dark:border-amber-800/40'
                        }`}
                      >
                        {c.status || 'PENDING'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 text-[11px] whitespace-nowrap">
                      {formatDate(c.created_at)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        to={`/diagnosis/${c.diagnosis_id || `DIAG-${c.case_id}`}`}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-sky-50 hover:bg-sky-100 dark:bg-sky-950/80 dark:hover:bg-sky-900/60 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800/60 text-xs font-semibold transition-all group-hover:border-sky-400"
                      >
                        <span>Diagnose</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="px-4 py-3 bg-slate-50/80 dark:bg-slate-900/60 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>
              Showing {filteredCases.length} of {cases.length} incidents
            </span>
            <span className="font-mono text-[11px]">
              Active Filter: {selectedCategory} | {selectedSeverity}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Cases;
