import React, { useState } from 'react';
import {
  Laptop,
  Server,
  Network,
  Shield,
  Layers,
  Zap,
  Play,
  CheckCircle2,
  AlertOctagon,
  Radio,
  Sparkles,
} from 'lucide-react';

export function TopologyViewer({ topologyString = '', addressingString = '' }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [isSimulatingTrace, setIsSimulatingTrace] = useState(false);
  const [traceStep, setTraceStep] = useState(0);

  // Convert topology string into structured node chain
  const nodes = React.useMemo(() => {
    if (!topologyString) return [];

    const rawParts = topologyString
      .split(/->|<->|-->|<--->|---\s*Fiber\s*Patch\s*--->|---/)
      .map((p) => p.trim())
      .filter(Boolean);

    if (rawParts.length === 0) {
      return [
        { id: 1, name: 'PC1-Student', model: 'Host Client', tag: 'VLAN 20', ip: '192.168.20.15', port: 'FastEthernet0' },
        { id: 2, name: 'SW1-2960', model: 'Catalyst 2960-24TT', tag: 'Trunk Gi0/1', ip: '192.168.20.2', port: 'Gi0/1', isFault: true },
        { id: 3, name: 'R1-1941', model: 'Cisco 1941 ISR', tag: 'Router-on-a-stick', ip: '192.168.20.1', port: 'GigabitEthernet0/0' },
        { id: 4, name: 'SW2-2960', model: 'Catalyst 2960-24TT', tag: 'Trunk Gi0/2', ip: '192.168.10.2', port: 'Gi0/2' },
        { id: 5, name: 'Server-Lab', model: 'NetAcad Server', tag: 'VLAN 10', ip: '192.168.10.50', port: 'FastEthernet0' },
      ];
    }

    return rawParts.map((part, index) => {
      const match = part.match(/(.*?)\s*\((.*?)\)/);
      const name = match ? match[1].trim() : part;
      const tag = match ? match[2].trim() : null;

      let model = 'Cisco Node';
      const lower = name.toLowerCase();
      if (lower.includes('pc') || lower.includes('host') || lower.includes('client')) model = 'PC-PT Endpoint';
      else if (lower.includes('sw') || lower.includes('switch')) model = 'Catalyst 2960-24TT';
      else if (lower.includes('r1') || lower.includes('router') || lower.includes('gw') || lower.includes('core')) model = 'Cisco 1941 / 2911 ISR';
      else if (lower.includes('server') || lower.includes('db')) model = 'Cisco Server-PT';
      else if (lower.includes('fw') || lower.includes('firewall') || lower.includes('asa')) model = 'Cisco ASA 5506-X';

      return {
        id: index + 1,
        name,
        model,
        tag: tag || (index === 0 ? 'Source Ingress' : index === rawParts.length - 1 ? 'Target Destination' : 'Transit Hop'),
        ip: index === 0 ? '192.168.20.15/24' : index === rawParts.length - 1 ? '192.168.10.50/24' : '10.255.0.1/30',
        port: index === 1 ? 'GigabitEthernet0/1' : `GigabitEthernet0/${index + 1}`,
        isFault: index === 1 || (index === 0 && rawParts.length <= 2),
      };
    });
  }, [topologyString]);

  const handleSimulateTrace = () => {
    if (isSimulatingTrace) return;
    setIsSimulatingTrace(true);
    setTraceStep(0);

    nodes.forEach((_, idx) => {
      setTimeout(() => {
        setTraceStep(idx + 1);
        if (idx === nodes.length - 1) {
          setTimeout(() => setIsSimulatingTrace(false), 900);
        }
      }, (idx + 1) * 600);
    });
  };

  const getDeviceIcon = (model = '') => {
    if (model.includes('PC') || model.includes('Host')) return Laptop;
    if (model.includes('Catalyst') || model.includes('Switch')) return Layers;
    if (model.includes('ISR') || model.includes('Router')) return Network;
    if (model.includes('Server')) return Server;
    if (model.includes('ASA') || model.includes('Firewall')) return Shield;
    return Network;
  };

  return (
    <div className="bg-slate-50 dark:bg-netacad-darkBg rounded-2xl border border-netacad-border dark:border-netacad-darkBorder p-5 space-y-4 shadow-sm">
      {/* Packet Tracer Header Bar */}
      <div className="flex items-center justify-between flex-wrap gap-2 pb-3 border-b border-netacad-border dark:border-netacad-darkBorder">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-netacad-green animate-pulse" />
          <span className="text-xs font-bold text-netacad-navy dark:text-white uppercase tracking-wider font-mono">
            Packet Tracer Logical Topology Canvas
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSimulateTrace}
            disabled={isSimulatingTrace}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-netacad-darkCard hover:bg-netacad-green/10 text-netacad-green border border-netacad-green/40 text-xs font-mono font-bold transition-all shadow-sm disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isSimulatingTrace ? `Simulating Hop ${traceStep}...` : 'Send Packet Tracer Ping'}</span>
          </button>
        </div>
      </div>

      {/* Visual Canvas with Packet Tracer Grid effect */}
      <div className="py-8 px-4 overflow-x-auto bg-white dark:bg-netacad-darkCard/70 rounded-2xl border border-netacad-border/80 dark:border-netacad-darkBorder relative">
        {/* Subtle grid pattern background */}
        <div
          className="absolute inset-0 opacity-40 pointer-events-none rounded-2xl"
          style={{
            backgroundImage: 'radial-gradient(circle, #94a3b8 1px, transparent 1px)',
            backgroundSize: '20px 20px',
          }}
        />

        <div className="flex items-center justify-between min-w-[660px] relative z-10">
          {/* Animated Connecting Cable (Straight-Through / Fiber) */}
          <div className="absolute top-7 left-12 right-12 h-1 bg-slate-200 dark:bg-slate-700 -translate-y-1/2 z-0 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-netacad-blue via-netacad-sky to-netacad-green transition-all duration-500 rounded-full"
              style={{
                width: isSimulatingTrace ? `${(traceStep / nodes.length) * 100}%` : '100%',
              }}
            />
          </div>

          {nodes.map((node, idx) => {
            const Icon = getDeviceIcon(node.model);
            const isSelected = selectedNode?.id === node.id;
            const isTraceActive = isSimulatingTrace && traceStep === idx + 1;

            return (
              <div key={node.id} className="relative z-10 flex flex-col items-center group">
                {/* Node Box */}
                <button
                  type="button"
                  onClick={() => setSelectedNode(node)}
                  className={`w-16 h-16 rounded-2xl flex flex-col items-center justify-center transition-all duration-300 border ${
                    isSelected
                      ? 'bg-netacad-blue/10 dark:bg-netacad-darkCard border-netacad-blue dark:border-netacad-sky ring-4 ring-netacad-blue/20 shadow-md scale-110'
                      : isTraceActive
                      ? 'bg-netacad-green/15 border-netacad-green ring-4 ring-netacad-green/30 scale-110'
                      : 'bg-white dark:bg-netacad-darkCard border-netacad-border dark:border-netacad-darkBorder hover:border-netacad-blue dark:hover:border-netacad-sky shadow-sm'
                  }`}
                >
                  <Icon
                    className={`w-7 h-7 ${
                      isSelected
                        ? 'text-netacad-blue dark:text-netacad-sky'
                        : isTraceActive
                        ? 'text-netacad-green'
                        : 'text-slate-700 dark:text-slate-200 group-hover:text-netacad-blue'
                    }`}
                  />
                </button>

                {/* Device Name */}
                <span className="mt-2.5 text-xs font-mono font-bold text-slate-900 dark:text-white text-center max-w-[120px] truncate">
                  {node.name}
                </span>

                {/* Device Model */}
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono text-center">
                  {node.model}
                </span>

                {/* Port / Tag */}
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full mt-1 bg-slate-100 dark:bg-netacad-darkBg border border-netacad-border dark:border-netacad-darkBorder text-netacad-blue dark:text-netacad-sky font-medium">
                  {node.tag}
                </span>

                {/* Link Port LED */}
                <span className="absolute top-0 right-0 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-netacad-green opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-netacad-green border border-white dark:border-netacad-darkCard"></span>
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode ? (
        <div className="p-4 bg-white dark:bg-netacad-darkCard rounded-xl border border-netacad-blue/30 dark:border-netacad-sky/40 flex items-center justify-between flex-wrap gap-4 text-xs shadow-sm">
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 rounded-xl bg-netacad-blue/10 dark:bg-netacad-sky/15 text-netacad-blue dark:text-netacad-sky border border-netacad-blue/20">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 dark:text-white font-mono text-sm">{selectedNode.name}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 dark:bg-netacad-darkBg text-netacad-blue dark:text-netacad-sky border border-netacad-border dark:border-netacad-darkBorder">
                  {selectedNode.model}
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-slate-600 dark:text-slate-300 font-mono mt-1">
                <span>Interface: <strong className="text-slate-900 dark:text-white">{selectedNode.port}</strong></span>
                <span>•</span>
                <span>IP Allocation: <strong className="text-netacad-blue dark:text-netacad-sky">{selectedNode.ip}</strong></span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setSelectedNode(null)}
            className="text-xs text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white font-mono px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-netacad-darkBg border border-netacad-border dark:border-netacad-darkBorder"
          >
            Close Inspector
          </button>
        </div>
      ) : (
        <div className="p-3 bg-white dark:bg-netacad-darkCard rounded-xl border border-netacad-border dark:border-netacad-darkBorder text-center text-slate-500 dark:text-slate-400 text-xs font-mono">
          Click any Cisco Packet Tracer device to inspect interface configuration and routing state
        </div>
      )}
    </div>
  );
}

export default TopologyViewer;
