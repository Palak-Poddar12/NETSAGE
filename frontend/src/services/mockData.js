/**
 * NetSage AI - Cisco Telemetry Dataset & Problem Statement Scenarios
 *
 * Aligned with AI Problem Statement:
 * 1. Evidence-Based Analysis
 * 2. Rule Engine Verification
 * 3. AI-Powered Diagnosis
 * 4. Human-in-the-Loop Review (Target KPI: >80% Agreement Rate)
 */

export const MOCK_METRICS = {
  total_cases: 30,
  accepted: 21,
  edited: 6,
  rejected: 3,
  agreement_rate: 82.5,
  target_kpi: 80.0,
  issue_distribution: [
    { category: 'VLAN', count: 8 },
    { category: 'Routing', count: 6 },
    { category: 'Inter-VLAN Routing', count: 4 },
    { category: 'DHCP', count: 3 },
    { category: 'DNS', count: 2 },
    { category: 'ACL', count: 3 },
    { category: 'NAT', count: 2 },
    { category: 'Wireless', count: 1 },
    { category: 'Gateway/Subnet', count: 3 },
    { category: 'Interface/Link', count: 4 },
  ],
  severity_distribution: [
    { severity: 'LOW', count: 4, fill: '#00bceb' },
    { severity: 'MEDIUM', count: 11, fill: '#f59e0b' },
    { severity: 'HIGH', count: 10, fill: '#f97316' },
    { severity: 'CRITICAL', count: 5, fill: '#ef4444' },
  ],
  common_rule_findings: [
    { rule_id: 'VLAN-002', name: 'VLAN Mismatch on Trunk Allowed List', occurrences: 9, category: 'VLAN', severity: 'HIGH' },
    { rule_id: 'DHCP-005', name: 'Missing IP Helper-Address on SVI', occurrences: 7, category: 'DHCP', severity: 'HIGH' },
    { rule_id: 'ROUTE-001', name: 'Missing Default / Static Route', occurrences: 6, category: 'Routing', severity: 'HIGH' },
    { rule_id: 'IFACE-003', name: 'Interface Administratively Down', occurrences: 6, category: 'Interface/Link', severity: 'MEDIUM' },
    { rule_id: 'ACL-004', name: 'Implicit Deny Dropping Port 443 Traffic', occurrences: 4, category: 'ACL', severity: 'CRITICAL' },
  ],
  conflicting_cases: [
    {
      case_id: 'CASE-019',
      symptom: 'Branch office cannot reach central database cluster',
      ai_diagnosis: 'OSPF MTU mismatch causing adjacency failure in Exchange state',
      rule_finding: 'ACL-004: Implicit Deny dropping IP protocol 89 (OSPF) on Gi0/0/1',
      conflict_reason: 'AI diagnosed MTU size issue while deterministic engine identified explicit ACL packet drop.',
      severity: 'CRITICAL',
    },
    {
      case_id: 'CASE-027',
      symptom: 'VoIP phones in VLAN 30 losing registration periodically',
      ai_diagnosis: 'Spanning-Tree topology change notifications resetting CAM table',
      rule_finding: 'DHCP-005: Lease duration exhausted with no renew ack received',
      conflict_reason: 'AI suggested L2 STP churn while deterministic inspection found DHCP pool exhaustion.',
      severity: 'HIGH',
    },
  ],
};

export const MOCK_CASES = [
  {
    case_id: 'CASE-001',
    category: 'VLAN',
    symptom: 'PC in VLAN 20 cannot communicate with server in VLAN 10.',
    topology: 'PC1 (VLAN 20) -> SW1 (Trunk Gi0/1) -> R1 (Router-on-a-stick) -> SW2 (Trunk) -> Server1 (VLAN 10)',
    addressing: 'PC1: 192.168.20.15/24, GW: 192.168.20.1 | Server1: 192.168.10.50/24, GW: 192.168.10.1',
    show_outputs: `SW1# show interfaces trunk
Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1,10

SW1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3
10   Engineering                      active    Gi0/4
20   Marketing                        active    Gi0/5`,
    expected_fault: 'VLAN 20 is not permitted on trunk link Gi0/1 between SW1 and R1.',
    osi_layer: 'Layer 2 (Data Link)',
    concept: '802.1Q Trunking & VLAN Allowed List Pruning',
    severity: 'HIGH',
    status: 'REVIEWED',
    created_at: '2026-08-28T14:22:00Z',
    diagnosis_id: 'DIAG-CASE-001',
  },
  {
    case_id: 'CASE-002',
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
end

SW-Core-3560# show ip dhcp conflict
No conflicts found.`,
    expected_fault: 'Missing "ip helper-address 10.10.1.100" command on Switch Virtual Interface (SVI) Vlan20.',
    osi_layer: 'Layer 3 (Network)',
    concept: 'DHCP Relay & SVI Broadcast Forwarding',
    severity: 'HIGH',
    status: 'REVIEWED',
    created_at: '2026-08-28T15:30:00Z',
    diagnosis_id: 'DIAG-CASE-002',
  },
  {
    case_id: 'CASE-003',
    category: 'Routing',
    symptom: 'Branch router cannot reach Corporate Headquarters core network.',
    topology: 'Branch-R1 (10.0.1.1) <-> WAN-Link (10.255.0.0/30) <-> HQ-Core-R1 (10.0.0.1)',
    addressing: 'Branch-R1 Gi0/0/0: 10.255.0.2/30, Loopback0: 10.0.1.1/24 | HQ-Core-R1 Gi0/0/0: 10.255.0.1/30',
    show_outputs: `Branch-R1# show ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area

Gateway of last resort is not set

      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.0.1.0/24 is directly connected, Loopback0
C        10.255.0.0/30 is directly connected, GigabitEthernet0/0/0

Branch-R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0/0   10.255.0.2      YES manual up                    up
Loopback0              10.0.1.1        YES manual up                    up`,
    expected_fault: 'No default gateway or static route configured towards HQ subnet 10.0.0.0/16.',
    osi_layer: 'Layer 3 (Network)',
    concept: 'Static Routing & Default Gateway',
    severity: 'HIGH',
    status: 'REVIEWED',
    created_at: '2026-08-28T16:45:00Z',
    diagnosis_id: 'DIAG-CASE-003',
  },
  {
    case_id: 'CASE-004',
    category: 'Interface/Link',
    symptom: 'Core switch Gi0/2 link between Building A and B is completely down.',
    topology: 'SW-Core-A (Gi0/2) <--- Fiber Patch ---> SW-Core-B (Gi0/2)',
    addressing: 'P2P Link: 10.100.1.0/30 (SW-Core-A: .1, SW-Core-B: .2)',
    show_outputs: `SW-Core-A# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/1     10.10.1.1       YES manual up                    up
GigabitEthernet0/2     10.100.1.1      YES manual administratively down down`,
    expected_fault: 'GigabitEthernet0/2 is administratively shutdown.',
    osi_layer: 'Layer 1 (Physical)',
    concept: 'Cisco IOS Interface State Administration',
    severity: 'MEDIUM',
    status: 'PENDING_REVIEW',
    created_at: '2026-08-29T09:15:00Z',
    diagnosis_id: 'DIAG-CASE-004',
  },
  {
    case_id: 'CASE-005',
    category: 'ACL',
    symptom: 'Finance workstation unable to reach HTTPS payment gateway.',
    topology: 'Finance-PC (172.16.10.25) -> SW-Acc -> R1 (Firewall/ACL) -> Internet',
    addressing: 'Finance Subnet: 172.16.10.0/24 | Payment API: 198.51.100.45:443',
    show_outputs: `R1# show access-lists 101
Extended IP access list 101
    10 permit tcp 172.16.10.0 0.0.0.255 any eq www (1542 matches)
    20 permit tcp 172.16.10.0 0.0.0.255 any eq domain (310 matches)
    30 deny ip any any (894 matches)`,
    expected_fault: 'ACL 101 permits port 80 (HTTP) and DNS but denies port 443 (HTTPS).',
    osi_layer: 'Layer 4 (Transport)',
    concept: 'Extended Access Control List Filtering',
    severity: 'CRITICAL',
    status: 'REVIEWED',
    created_at: '2026-08-29T11:00:00Z',
    diagnosis_id: 'DIAG-CASE-005',
  },
];

export const MOCK_DIAGNOSES = {
  'DIAG-CASE-001': {
    diagnosis_id: 'DIAG-CASE-001',
    case_id: 'CASE-001',
    status: 'DIAGNOSIS_SUPPORTED',
    confidence: 0.94,
    created_at: '2026-08-28T14:22:15Z',
    case_summary: {
      category: 'VLAN',
      symptom: 'PC in VLAN 20 cannot communicate with server in VLAN 10.',
      severity: 'HIGH',
      osi_layer: 'Layer 2 (Data Link)',
    },
    network_evidence: {
      topology: 'PC1 (VLAN 20) -> SW1 (Trunk Gi0/1) -> R1 (Router-on-a-stick) -> SW2 (Trunk) -> Server1 (VLAN 10)',
      addressing: 'PC1: 192.168.20.15/24, GW: 192.168.20.1 | Server1: 192.168.10.50/24, GW: 192.168.10.1',
      show_outputs: `SW1# show interfaces trunk
Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1,10

SW1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3
10   Engineering                      active    Gi0/4
20   Marketing                        active    Gi0/5`,
    },
    rule_engine_findings: [
      {
        rule_id: 'VLAN-002',
        name: 'VLAN Pruning / Allowed List Exclusion',
        category: 'VLAN',
        severity: 'HIGH',
        status: 'VIOLATION',
        message: 'VLAN 20 is configured in local database but explicitly excluded from allowed VLAN list on trunk Gi0/1.',
        evidence: 'show interfaces trunk indicates "Vlans allowed on trunk: 1,10". VLAN 20 is missing.',
      },
      {
        rule_id: 'IFACE-001',
        name: 'Trunk Interface Link Operational State',
        category: 'Interface/Link',
        severity: 'LOW',
        status: 'PASSED',
        message: 'Trunk interface Gi0/1 is in operational 802.1Q trunking state.',
        evidence: 'Port Gi0/1 status is trunking.',
      },
    ],
    ai_diagnosis: {
      root_cause: 'VLAN 20 traffic is dropped at the switch trunk port Gi0/1 because the trunk allowed VLAN list explicitly restricts traffic to VLANs 1 and 10, preventing Inter-VLAN routing through R1.',
      category: 'VLAN',
      osi_layer: 'Layer 2 (Data Link)',
      confidence: 0.94,
      evidence_correlation: 'The command "show interfaces trunk" directly confirms "Vlans allowed on trunk: 1,10". PC1 resides in VLAN 20 (Marketing), so frames are discarded on ingress/egress across Gi0/1 towards router R1.',
      alternative_causes: [
        'Missing sub-interface encapsulation dot1Q 20 on Router R1',
        'Incorrect default gateway IP configured on PC1',
      ],
      missing_evidence: 'Show command output from upstream Router R1 (show ip interface brief, show running-config interface) would verify sub-interface state.',
      next_diagnostic_command: 'SW1# show running-config interface GigabitEthernet0/1\nR1# show ip interface brief',
      proposed_fix: `SW1# configure terminal
SW1(config)# interface GigabitEthernet 0/1
SW1(config-if)# switchport trunk allowed vlan add 20
SW1(config-if)# end
SW1# write memory`,
      verification_command: `SW1# show interfaces trunk
PC1> ping 192.168.20.1
PC1> ping 192.168.10.50`,
    },
    review: {
      status: 'ACCEPTED',
      reviewer: 'Senior NetOps Engineer',
      timestamp: '2026-08-28T15:10:00Z',
      comment: 'Verified against Cisco trunking documentation. Correct diagnosis.',
    },
  },
  'DIAG-CASE-002': {
    diagnosis_id: 'DIAG-CASE-002',
    case_id: 'CASE-002',
    status: 'DIAGNOSIS_SUPPORTED',
    confidence: 0.96,
    created_at: '2026-08-28T15:30:10Z',
    case_summary: {
      category: 'DHCP',
      symptom: 'Host in VLAN 20 cannot receive IP address from central DHCP server.',
      severity: 'HIGH',
      osi_layer: 'Layer 3 (Network)',
    },
    network_evidence: {
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
    },
    rule_engine_findings: [
      {
        rule_id: 'DHCP-005',
        name: 'Missing IP Helper-Address on SVI',
        category: 'DHCP',
        severity: 'HIGH',
        status: 'VIOLATION',
        message: 'No "ip helper-address" configured under SVI interface Vlan20 to relay DHCP DISCOVER broadcasts to external DHCP server.',
        evidence: 'show running-config interface Vlan20 shows no ip helper-address statements.',
      },
    ],
    ai_diagnosis: {
      root_cause: 'DHCP DISCOVER broadcast packets from VLAN 20 clients are dropped by the Layer 3 switch SVI because no "ip helper-address" relay agent is configured to unicast requests to 10.10.1.100.',
      category: 'DHCP',
      osi_layer: 'Layer 3 (Network)',
      confidence: 0.96,
      evidence_correlation: 'DHCP is a Layer 2 broadcast (255.255.255.255) by default and does not cross Layer 3 router boundaries without an active IP helper relay address configured on the default gateway SVI.',
      alternative_causes: ['DHCP pool scope exhaustion on server 10.10.1.100', 'Access-list dropping UDP port 67/68'],
      missing_evidence: 'Show ip dhcp binding on DHCP server.',
      next_diagnostic_command: 'SW-Core-3560# show ip dhcp relay information trusted-sources',
      proposed_fix: `SW-Core-3560# configure terminal
SW-Core-3560(config)# interface Vlan20
SW-Core-3560(config-if)# ip helper-address 10.10.1.100
SW-Core-3560(config-if)# end
SW-Core-3560# write memory`,
      verification_command: `SW-Core-3560# show running-config interface Vlan20 | include helper
Host-PC> ipconfig /renew`,
    },
    review: {
      status: 'ACCEPTED',
      reviewer: 'Cisco TAC Escalation Engineer',
      timestamp: '2026-08-28T16:00:00Z',
      comment: 'Accurately detected missing DHCP relay on core switch.',
    },
  },
};
