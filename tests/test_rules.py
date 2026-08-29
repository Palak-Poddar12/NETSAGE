import pytest
from app.rules.duplicate_ip import DuplicateIPRule
from app.rules.invalid_subnet import InvalidSubnetRule
from app.rules.gateway_mismatch import GatewayMismatchRule
from app.rules.interface_down import InterfaceDownRule
from app.rules.missing_vlan import MissingVLANRule
from app.rules.trunk_vlan_mismatch import TrunkVLANMismatchRule
from app.rules.missing_route import MissingRouteRule
from app.rules.acl_deny import ACLDenyRule
from app.rules.dhcp_inconsistency import DHCPInconsistencyRule
from app.rules.nat_inconsistency import NATInconsistencyRule
from app.rules.engine import rule_engine

# 1. Duplicate IP
def test_duplicate_ip_detected():
    rule = DuplicateIPRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.50"},
        {"device": "Host-B", "interface": "eth0", "ip_address": "192.168.1.50"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert not finding.passed
    assert finding.severity == "critical"
    assert "192.168.1.50" in finding.details

def test_duplicate_ip_passed():
    rule = DuplicateIPRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.50"},
        {"device": "Host-B", "interface": "eth0", "ip_address": "192.168.1.51"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert finding.passed

# 2. Invalid Subnet
def test_invalid_subnet_network_address_detected():
    rule = InvalidSubnetRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.0/24"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert not finding.passed
    assert "network address" in finding.details

def test_invalid_subnet_broadcast_address_detected():
    rule = InvalidSubnetRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.255", "subnet_mask": "255.255.255.0"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert not finding.passed
    assert "broadcast address" in finding.details

def test_invalid_subnet_passed():
    rule = InvalidSubnetRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.100/24"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert finding.passed

# 3. Gateway Mismatch
def test_gateway_mismatch_detected():
    rule = GatewayMismatchRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.50/24", "default_gateway": "192.168.2.1"},
        {"device": "R1", "interface": "Gig0/0", "ip_address": "192.168.1.1/24"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert not finding.passed
    assert "outside local subnet" in finding.details

def test_gateway_mismatch_passed():
    rule = GatewayMismatchRule()
    addressing = [
        {"device": "Host-A", "interface": "eth0", "ip_address": "192.168.1.50/24", "default_gateway": "192.168.1.1"},
        {"device": "R1", "interface": "Gig0/0", "ip_address": "192.168.1.1/24"}
    ]
    finding = rule.evaluate({}, addressing, {})
    assert finding.passed

# 4. Interface Down
def test_interface_down_detected():
    rule = InterfaceDownRule()
    show_outputs = {
        "R1": {
            "show_ip_interface_brief": "GigabitEthernet0/1 192.168.1.1 YES manual administratively down down"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert not finding.passed
    assert "administratively down" in finding.details

def test_interface_down_passed():
    rule = InterfaceDownRule()
    show_outputs = {
        "R1": {
            "show_ip_interface_brief": "GigabitEthernet0/1 192.168.1.1 YES manual up up"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert finding.passed

# 5. Missing VLAN
def test_missing_vlan_detected():
    rule = MissingVLANRule()
    topology = {
        "links": [{"source": "Host-A", "target": "SW1"}]
    }
    addressing = [
        {"device": "Host-A", "interface": "eth0", "vlan": 99}
    ]
    show_outputs = {
        "SW1": {
            "show_vlan_brief": "1 default active Gi0/1\n10 Users active Gi0/2"
        }
    }
    finding = rule.evaluate(topology, addressing, show_outputs)
    assert not finding.passed
    assert "VLAN 99" in finding.details

def test_missing_vlan_passed():
    rule = MissingVLANRule()
    topology = {
        "links": [{"source": "Host-A", "target": "SW1"}]
    }
    addressing = [
        {"device": "Host-A", "interface": "eth0", "vlan": 10}
    ]
    show_outputs = {
        "SW1": {
            "show_vlan_brief": "1 default active Gi0/1\n10 Users active Gi0/2"
        }
    }
    finding = rule.evaluate(topology, addressing, show_outputs)
    assert finding.passed

# 6. Trunk VLAN Mismatch
def test_trunk_vlan_mismatch_detected():
    rule = TrunkVLANMismatchRule()
    topology = {
        "links": [{"source": "SW1", "source_interface": "Gi0/24", "target": "SW2", "target_interface": "Gi0/24"}]
    }
    show_outputs = {
        "SW1": {
            "show_interfaces_trunk": "Gi0/24 on 802.1q trunking 10\nGi0/24 10,20"
        },
        "SW2": {
            "show_interfaces_trunk": "Gi0/24 on 802.1q trunking 20\nGi0/24 10,20"
        }
    }
    finding = rule.evaluate(topology, [], show_outputs)
    assert not finding.passed
    assert "Native VLAN mismatch" in finding.details

def test_trunk_vlan_mismatch_passed():
    rule = TrunkVLANMismatchRule()
    topology = {
        "links": [{"source": "SW1", "source_interface": "Gi0/24", "target": "SW2", "target_interface": "Gi0/24"}]
    }
    show_outputs = {
        "SW1": {
            "show_interfaces_trunk": "Gi0/24 on 802.1q trunking 1\nGi0/24 10,20"
        },
        "SW2": {
            "show_interfaces_trunk": "Gi0/24 on 802.1q trunking 1\nGi0/24 10,20"
        }
    }
    finding = rule.evaluate(topology, [], show_outputs)
    assert finding.passed

# 7. Missing Route
def test_missing_route_detected():
    rule = MissingRouteRule()
    addressing = [
        {"device": "Server", "ip_address": "172.16.50.10/24"}
    ]
    show_outputs = {
        "R1": {
            "show_ip_route": "Gateway of last resort is not set\nC 192.168.1.0/24 is directly connected"
        }
    }
    finding = rule.evaluate({}, addressing, show_outputs)
    assert not finding.passed
    assert "172.16.50.0/24" in finding.details

def test_missing_route_passed_with_default():
    rule = MissingRouteRule()
    addressing = [
        {"device": "Server", "ip_address": "172.16.50.10/24"}
    ]
    show_outputs = {
        "R1": {
            "show_ip_route": "S* 0.0.0.0/0 [1/0] via 10.0.0.1"
        }
    }
    finding = rule.evaluate({}, addressing, show_outputs)
    assert finding.passed

# 8. ACL Deny
def test_acl_deny_detected():
    rule = ACLDenyRule()
    show_outputs = {
        "R1": {
            "show_access_lists": "Extended IP access list 101\n 10 deny ip any any (452 matches)"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert not finding.passed
    assert "active deny rule" in finding.details or "deny" in finding.details

def test_acl_deny_passed():
    rule = ACLDenyRule()
    show_outputs = {
        "R1": {
            "show_access_lists": "Extended IP access list 101\n 10 permit ip 192.168.1.0 0.0.0.255 any (1020 matches)"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert finding.passed

# 9. DHCP Inconsistency
def test_dhcp_inconsistency_detected():
    rule = DHCPInconsistencyRule()
    show_outputs = {
        "R1": {
            "show_running_config": "ip dhcp pool LAN\n network 192.168.1.0 255.255.255.0\n default-router 10.0.0.1"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert not finding.passed
    assert "outside pool subnet" in finding.details

def test_dhcp_inconsistency_passed():
    rule = DHCPInconsistencyRule()
    show_outputs = {
        "R1": {
            "show_running_config": "ip dhcp pool LAN\n network 192.168.1.0 255.255.255.0\n default-router 192.168.1.1"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert finding.passed

# 10. NAT Inconsistency
def test_nat_inconsistency_missing_outside():
    rule = NATInconsistencyRule()
    show_outputs = {
        "R1": {
            "show_running_config": "interface Gig0/0\n ip nat inside\ninterface Gig0/1\n ip address 203.0.113.1 255.255.255.0\nip nat inside source list 1 interface Gig0/1 overload"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert not finding.passed
    assert "ip nat outside" in finding.details

def test_nat_inconsistency_passed():
    rule = NATInconsistencyRule()
    show_outputs = {
        "R1": {
            "show_running_config": "interface Gig0/0\n ip nat inside\ninterface Gig0/1\n ip nat outside\nip nat inside source list 1 interface Gig0/1 overload"
        }
    }
    finding = rule.evaluate({}, [], show_outputs)
    assert finding.passed

def test_rule_engine_runs_all_10_rules():
    findings = rule_engine.run_all({}, [], {})
    assert len(findings) == 10
    rule_ids = {f.rule_id for f in findings}
    expected_ids = {
        "duplicate_ip", "invalid_subnet", "gateway_mismatch", "interface_down",
        "missing_vlan", "trunk_vlan_mismatch", "missing_route", "acl_deny",
        "dhcp_inconsistency", "nat_inconsistency"
    }
    assert rule_ids == expected_ids
