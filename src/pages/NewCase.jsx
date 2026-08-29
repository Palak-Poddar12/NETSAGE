import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PlusCircle,
  Terminal,
  Network,
  Server,
  Layers,
  AlertCircle,
  CheckCircle,
  FileCode,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  HelpCircle,
} from 'lucide-react';
import { CATEGORIES, SEVERITIES, OSI_LAYERS } from '../utils/constants';
import { useCaseContext } from '../context/CaseContext';
import { useToast } from '../components/Toast';

export function NewCase() {
  const navigate = useNavigate();
  const { addCase } = useCaseContext();
  const { addToast } = useToast();

  // Form State
  const [formData, setFormData] = useState({
    case_id: `CASE-${Math.floor(100 + Math.random() * 900)}`,
    category: 'VLAN',
    symptom: '',
    topology: '',
    addressing: '',
    show_outputs: '',
    expected_fault: '',
    osi_layer: 'Layer 2 (Data Link)',
    concept: '',
    severity: 'HIGH',
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successInfo, setSuccessInfo] = useState(null);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const presetIncidents = [
    {
      title: 'VLAN 802.1Q Trunk Pruning Fault',
      badge: 'VLAN / Trunking',
      data: {
        case_id: `CASE-051`,
        category: 'VLAN',
        symptom: 'PC in Marketing VLAN 20 cannot reach Core Database in Engineering VLAN 10.',
        topology: 'Host-Marketing (VLAN 20) -> SW-Catalyst-1 (Trunk Gi0/1) -> R1-ISR-4331 -> SW-Catalyst-2 -> DB-Server (VLAN 10)',
        addressing: 'Host-PC: 192.168.20.15/24, GW: 192.168.20.1 | DB-Server: 192.168.10.50/24, GW: 192.168.10.1',
        show_outputs: `SW-Catalyst-1# show interfaces trunk
Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1,10

SW-Catalyst-1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3
10   Engineering                      active    Gi0/4
20   Marketing                        active    Gi0/5`,
        expected_fault: 'VLAN 20 is not permitted on trunk link Gi0/1 between Catalyst switch and ISR router.',
        osi_layer: 'Layer 2 (Data Link)',
        concept: '802.1Q Trunk Allowed List Pruning',
        severity: 'HIGH',
      },
    },
    {
      title: 'DHCP Relay Missing on Core SVI',
      badge: 'DHCP / Relay',
      data: {
        case_id: `CASE-052`,
        category: 'DHCP',
        symptom: 'Host in VLAN 20 cannot receive IP address from central DHCP server.',
        topology: 'Host-PC (VLAN 20) -> SW-Core-3560 (SVI Vlan20) -> R1 -> DHCP-Server (10.10.1.100)',
        addressing: 'Vlan20 SVI: 192.168.20.1/24 | DHCP Server IP: 10.10.1.100',
        show_outputs: `SW-Core-3560# show running-config interface Vlan20
Building configuration...
Current configuration : 110 bytes
!
interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 no ip redirects
!
end`,
        expected_fault: 'Missing "ip helper-address 10.10.1.100" command on Switch Virtual Interface (SVI) Vlan20.',
        osi_layer: 'Layer 3 (Network)',
        concept: 'DHCP Relay & SVI Broadcast Forwarding',
        severity: 'HIGH',
      },
    },
    {
      title: 'OSPF ExStart / MTU Size Mismatch',
      badge: 'OSPF / L3',
      data: {
        case_id: `CASE-053`,
        category: 'Routing',
        symptom: 'OSPF neighbor adjacency stuck in ExStart state across WAN point-to-point link.',
        topology: 'Branch-ISR-4321 (Gi0/0/1) <--- MetroEthernet Trunk ---> HQ-ASR-1001X (Gi0/0/1)',
        addressing: 'P2P Link: 10.255.0.0/30 (Branch: .1, HQ: .2) | Branch MTU: 1500, HQ MTU: 1492',
        show_outputs: `Branch-ISR-4321# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.0.0.1          1   EXSTART/  -     00:00:33    10.255.0.2      GigabitEthernet0/0/1

HQ-ASR-1001X# show ip interface GigabitEthernet0/0/1 | include MTU
  MTU is 1492 bytes

Branch-ISR-4321# show ip interface GigabitEthernet0/0/1 | include MTU
  MTU is 1500 bytes`,
        expected_fault: 'Interface MTU mismatch prevents OSPF Database Description (DBD) packet exchange.',
        osi_layer: 'Layer 3 (Network)',
        concept: 'OSPF DBD MTU Negotiation Deadlock',
        severity: 'HIGH',
      },
    },
  ];

  const handleApplyPreset = (preset) => {
    setFormData(preset.data);
    addToast(`Loaded incident scenario: ${preset.title}`, 'info');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.case_id.trim()) {
      setError('Case ID is required.');
      return;
    }
    if (!formData.symptom.trim()) {
      setError('Network fault symptom is required.');
      return;
    }
    if (!formData.show_outputs.trim()) {
      setError('At least one Cisco show command output is required.');
      return;
    }

    setSubmitting(true);

    try {
      const created = addCase(formData);
      setSuccessInfo(created);
      addToast(`Incident ${created.case_id} registered! Synthesizing diagnosis...`, 'success');

      setTimeout(() => {
        navigate(`/diagnosis/${created.diagnosis_id}`);
      }, 1000);
    } catch (err) {
      setError(err.message || 'Failed to create case. Please retry.');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Zap className="w-4 h-4 text-sky-600 dark:text-sky-400" />
          <span className="text-xs font-mono font-bold tracking-wider text-sky-600 dark:text-sky-400 uppercase">
            Cisco TAC Telemetry Ingestion
          </span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Submit Troubleshooting Incident
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-sans">
          Provide Cisco IOS show command outputs, network topology, and symptoms for real-time automated diagnosis.
        </p>
      </div>

      {/* Quick Templates Selector */}
      <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3 shadow-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-mono font-bold text-slate-800 dark:text-white uppercase">
            <Sparkles className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            <span>Pre-Engineered Cisco Problem Scenarios</span>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">1-Click Load</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {presetIncidents.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyPreset(preset)}
              className="text-left p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 hover:bg-sky-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 hover:border-sky-400 transition-all group shadow-subtle"
            >
              <div className="text-[10px] font-mono font-bold text-sky-600 dark:text-sky-400 mb-1">
                {preset.badge}
              </div>
              <div className="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-sky-600 dark:group-hover:text-sky-400 transition-colors line-clamp-1">
                {preset.title}
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                {preset.data.symptom}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Form Card */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-6 shadow-card">
        {/* Section 1: Identification & Taxonomy */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800 text-xs font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 font-mono">
            <Layers className="w-4 h-4" />
            <span>Incident Taxonomy & Layer</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Case ID */}
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Incident ID <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={formData.case_id}
                onChange={(e) => handleChange('case_id', e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-sky-600 dark:text-sky-400 focus:outline-none focus:border-sky-500 font-bold"
                placeholder="e.g. CASE-042"
                required
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Category <span className="text-rose-500">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => handleChange('category', e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-sky-500 font-mono"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity */}
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Severity <span className="text-rose-500">*</span>
              </label>
              <select
                value={formData.severity}
                onChange={(e) => handleChange('severity', e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-sky-500 font-mono"
              >
                {SEVERITIES.map((sev) => (
                  <option key={sev} value={sev}>
                    {sev}
                  </option>
                ))}
              </select>
            </div>

            {/* OSI Layer */}
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                OSI Layer
              </label>
              <select
                value={formData.osi_layer}
                onChange={(e) => handleChange('osi_layer', e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-sky-500 font-mono"
              >
                {OSI_LAYERS.map((layer) => (
                  <option key={layer} value={layer}>
                    {layer}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Technical Concept */}
          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Network Feature / Concept
            </label>
            <input
              type="text"
              value={formData.concept}
              onChange={(e) => handleChange('concept', e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-sky-500 font-mono"
              placeholder="e.g. 802.1Q Trunking, OSPF DBD Exchange, Extended ACL"
            />
          </div>
        </div>

        {/* Section 2: Symptom & Fault Hypothesis */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800 text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400 font-mono">
            <AlertCircle className="w-4 h-4" />
            <span>Incident Symptoms & Fault Hypothesis</span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Observed Symptom <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={formData.symptom}
              onChange={(e) => handleChange('symptom', e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-sky-500"
              placeholder="e.g. PC in Marketing VLAN 20 cannot communicate with server in VLAN 10."
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Expected Fault (Optional Engineer Note)
            </label>
            <input
              type="text"
              value={formData.expected_fault}
              onChange={(e) => handleChange('expected_fault', e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-sky-500"
              placeholder="e.g. VLAN 20 is not permitted on trunk link Gi0/1 between SW1 and R1."
            />
          </div>
        </div>

        {/* Section 3: Topology & Addressing */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800 text-xs font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 font-mono">
            <Network className="w-4 h-4" />
            <span>Topology & Addressing Details</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Topology Description (use &rarr; between nodes)
              </label>
              <textarea
                rows={3}
                value={formData.topology}
                onChange={(e) => handleChange('topology', e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-3 text-xs text-slate-900 dark:text-white font-mono placeholder-slate-400 focus:outline-none focus:border-sky-500"
                placeholder="e.g. PC1 (VLAN 20) -> SW-Catalyst-1 -> R1-ISR -> Server1 (VLAN 10)"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                IP Addressing Information
              </label>
              <textarea
                rows={3}
                value={formData.addressing}
                onChange={(e) => handleChange('addressing', e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-3 text-xs text-slate-900 dark:text-white font-mono placeholder-slate-400 focus:outline-none focus:border-sky-500"
                placeholder="e.g. PC1: 192.168.20.15/24, GW: 192.168.20.1 | Server: 192.168.10.50/24"
              />
            </div>
          </div>
        </div>

        {/* Section 4: Cisco Show Command Outputs */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 font-mono">
              <Terminal className="w-4 h-4" />
              <span>Cisco Show Command Outputs <span className="text-rose-500">*</span></span>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              Paste CLI outputs
            </span>
          </div>

          <div>
            <textarea
              rows={8}
              value={formData.show_outputs}
              onChange={(e) => handleChange('show_outputs', e.target.value)}
              className="w-full cisco-terminal bg-slate-900 dark:bg-[#080c14] text-sky-300 border-slate-700 focus:outline-none focus:border-sky-400 selection:bg-sky-800/40"
              placeholder={`SW1# show interfaces trunk
SW1# show vlan brief
R1# show ip interface brief
R1# show ip route`}
              required
            />
          </div>
        </div>

        {/* Error / Success Feedback */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/80 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successInfo && (
          <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              <span>Incident created successfully! Opening diagnostic workspace...</span>
            </div>
            <span className="font-mono text-xs font-bold">{successInfo.case_id}</span>
          </div>
        )}

        {/* Submit Action */}
        <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-end gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold uppercase tracking-wider shadow-sm hover:shadow transition-all active:scale-95 disabled:opacity-50"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{submitting ? 'Synthesizing...' : 'CREATE & DIAGNOSE CASE'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}

export default NewCase;
