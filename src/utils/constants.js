export const CATEGORIES = [
  'VLAN',
  'Routing',
  'Inter-VLAN Routing',
  'DHCP',
  'DNS',
  'ACL',
  'NAT',
  'Wireless',
  'Gateway/Subnet',
  'Interface/Link',
];

export const SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export const OSI_LAYERS = [
  'Layer 1 (Physical)',
  'Layer 2 (Data Link)',
  'Layer 3 (Network)',
  'Layer 4 (Transport)',
  'Layer 7 (Application)',
];

export const DIAGNOSIS_STATUS = {
  SUPPORTED: 'DIAGNOSIS_SUPPORTED',
  PARTIALLY_SUPPORTED: 'PARTIALLY_SUPPORTED',
  INSUFFICIENT: 'INSUFFICIENT_EVIDENCE',
  CONFLICTING: 'CONFLICTING_EVIDENCE',
};

export const REVIEW_STATUS = {
  PENDING: 'PENDING_REVIEW',
  ACCEPTED: 'ACCEPTED',
  EDITED: 'EDITED',
  REJECTED: 'REJECTED',
};
