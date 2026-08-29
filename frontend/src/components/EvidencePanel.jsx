import React, { useState } from 'react';
import {
  Terminal,
  Copy,
  Check,
  Download,
  Search,
  Layers,
  Network,
  Server,
  FileCode,
} from 'lucide-react';
import { TopologyViewer } from './TopologyViewer';
import { useToast } from './Toast';

export function EvidencePanel({ evidence = {} }) {
  const { addToast } = useToast();
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('outputs'); // 'outputs' | 'topology' | 'addressing'
  const [searchFilter, setSearchFilter] = useState('');

  const { topology, addressing, show_outputs = '' } = evidence;

  const handleCopyOutputs = () => {
    if (!show_outputs) return;
    navigator.clipboard.writeText(show_outputs);
    setCopied(true);
    addToast('Raw Cisco show command outputs copied to clipboard.', 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadLog = () => {
    const blob = new Blob([show_outputs || 'No outputs'], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cisco-diagnostic-evidence-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addToast('Downloaded diagnostic evidence log file.', 'info');
  };

  // Highlight keywords or filter lines in show output
  const renderFormattedTerminal = () => {
    if (!show_outputs) return <div className="text-slate-400"># No command outputs provided.</div>;

    const lines = show_outputs.split('\n');
    return lines.map((line, idx) => {
      const isCommand = line.includes('#') || line.includes('>');
      const isDown = line.toLowerCase().includes('down') || line.toLowerCase().includes('deny');
      const isUp = line.toLowerCase().includes('up') && line.toLowerCase().includes('up');

      const matchesSearch = searchFilter && line.toLowerCase().includes(searchFilter.toLowerCase());

      return (
        <div
          key={idx}
          className={`px-2 py-0.5 leading-relaxed font-mono text-xs ${
            matchesSearch
              ? 'bg-amber-500/20 text-amber-200 font-bold'
              : isCommand
              ? 'text-emerald-400 font-bold bg-cisco-dark/60'
              : isDown
              ? 'text-rose-400'
              : isUp
              ? 'text-cyan-300'
              : 'text-slate-300'
          }`}
        >
          <span className="text-slate-400 select-none mr-3 text-[10px] inline-block w-6 text-right">
            {idx + 1}
          </span>
          {line}
        </div>
      );
    });
  };

  return (
    <div className="bg-cisco-navy rounded-2xl border border-cisco-border overflow-hidden shadow-cisco-card">
      {/* Header Tabs */}
      <div className="px-5 py-3.5 border-b border-cisco-border bg-cisco-dark/80 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cisco-sky" />
          <h3 className="text-sm font-bold text-white tracking-tight">
            Cisco Telemetry & Evidence Inspector
          </h3>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center gap-1 bg-cisco-surface p-1 rounded-xl border border-cisco-border text-xs">
          <button
            onClick={() => setActiveTab('outputs')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'outputs'
                ? 'bg-cisco-card text-cisco-sky shadow-cisco-glow border border-cisco-sky/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Show Outputs
          </button>
          <button
            onClick={() => setActiveTab('topology')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'topology'
                ? 'bg-cisco-card text-cisco-sky shadow-cisco-glow border border-cisco-sky/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Topology Map
          </button>
          <button
            onClick={() => setActiveTab('addressing')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'addressing'
                ? 'bg-cisco-card text-cisco-sky shadow-cisco-glow border border-cisco-sky/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Addressing
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-5">
        {/* Terminal Show Command Outputs */}
        {activeTab === 'outputs' && (
          <div className="space-y-3">
            {/* Terminal Actions Bar */}
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="relative flex-1 max-w-xs">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  placeholder="Filter outputs (e.g. down, vlan, MTU)..."
                  className="w-full bg-cisco-dark border border-cisco-border rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cisco-sky font-mono"
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownloadLog}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cisco-surface hover:bg-cisco-hover text-slate-300 hover:text-white text-xs font-mono border border-cisco-border transition-colors"
                  title="Download Raw Output Log"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export</span>
                </button>

                <button
                  onClick={handleCopyOutputs}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cisco-surface hover:bg-cisco-hover text-cisco-sky text-xs font-mono font-bold border border-cisco-border transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Buffer</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Monospace Cisco Terminal Window */}
            <div className="bg-cisco-dark rounded-xl border border-cisco-border overflow-hidden">
              <div className="px-4 py-2 bg-cisco-surface/80 border-b border-cisco-border flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
                  <span className="ml-2 text-slate-300 font-bold">Cisco IOS-XE Diagnostic Shell</span>
                </div>
                <span>VT100 Emulation</span>
              </div>

              <div className="p-3 max-h-96 overflow-y-auto font-mono text-xs selection:bg-cisco-sky/30">
                {renderFormattedTerminal()}
              </div>
            </div>
          </div>
        )}

        {/* Visual Topology */}
        {activeTab === 'topology' && (
          <TopologyViewer
            topologyString={topology}
            addressingString={addressing}
          />
        )}

        {/* Addressing Table */}
        {activeTab === 'addressing' && (
          <div className="bg-cisco-dark rounded-xl border border-cisco-border p-5 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cisco-sky font-mono">
              <Server className="w-4 h-4" />
              <span>IP Subnets & Interface Allocations</span>
            </div>
            <pre className="p-4 bg-cisco-surface rounded-lg border border-cisco-border font-mono text-xs text-cisco-sky leading-relaxed whitespace-pre-wrap">
              {addressing || 'No addressing details specified.'}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default EvidencePanel;
