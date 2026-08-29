import ipaddress, re
from typing import List, Dict

def check_duplicate_ips(outputs: List[str]) -> List[Dict]:
    ips = {}
    for out in outputs:
        for m in re.finditer(r'(\d+\.\d+\.\d+\.\d+)', out):
            ip = m.group(1)
            if ip in ips:
                return [{"rule_id":"DUPLICATE_IP","category":"IP","severity":"HIGH","message":f"Duplicate IP {ip}","evidence":"Multiple devices claim same IP"}]
            ips[ip] = True
    return []

def check_invalid_ips(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        for m in re.finditer(r'(\d+\.\d+\.\d+\.\d+)', out):
            try: ipaddress.ip_address(m.group(1))
            except: findings.append({"rule_id":"INVALID_IP","category":"IP","severity":"HIGH","message":f"Invalid IP {m.group(1)}","evidence":"IP address format is invalid"})
    return findings

def check_interface_down(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        for line in out.splitlines():
            if "administratively down" in line.lower():
                iface = line.split()[0] if line.split() else "unknown"
                findings.append({"rule_id":"IFACE_ADMIN_DOWN","category":"INTERFACE","severity":"MEDIUM","message":f"{iface} administratively down","evidence":line.strip()})
            elif "down" in line.lower() and "up" not in line.lower() and "line protocol" in line.lower():
                iface = line.split()[0] if line.split() else "unknown"
                findings.append({"rule_id":"IFACE_DOWN","category":"INTERFACE","severity":"HIGH","message":f"{iface} operationally down","evidence":line.strip()})
    return findings

def check_vlan_missing(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        if "show vlan brief" in out.lower() or "vlan" in out.lower():
            if "vlan 30" not in out.lower() and "vlan30" not in out.lower():
                if any("vlan" in o.lower() for o in outputs):
                    findings.append({"rule_id":"VLAN_MISSING","category":"VLAN","severity":"HIGH","message":"VLAN 30 is missing","evidence":"show vlan brief does not contain VLAN 30"})
    return findings

def check_missing_route(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        if "show ip route" in out.lower():
            if "0.0.0.0" not in out and "gateway of last resort" not in out.lower():
                findings.append({"rule_id":"MISSING_DEFAULT_ROUTE","category":"ROUTING","severity":"HIGH","message":"Missing default route","evidence":"No default route in show ip route"})
    return findings

def check_acl_deny(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        if "show access-lists" in out.lower():
            if "deny" in out.lower():
                findings.append({"rule_id":"ACL_DENY","category":"ACL","severity":"MEDIUM","message":"ACL contains deny statements","evidence":"show access-lists shows deny entries"})
    return findings

def check_dhcp_issues(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        if "show ip dhcp binding" in out.lower():
            if not out.strip().replace("show ip dhcp binding","").strip():
                findings.append({"rule_id":"DHCP_NO_BINDINGS","category":"DHCP","severity":"MEDIUM","message":"No DHCP bindings found","evidence":"show ip dhcp binding is empty"})
    return findings

def check_nat_issues(outputs: List[str]) -> List[Dict]:
    findings = []
    for out in outputs:
        if "show ip nat translations" in out.lower():
            if not out.strip().replace("show ip nat translations","").strip():
                findings.append({"rule_id":"NAT_NO_TRANS","category":"NAT","severity":"MEDIUM","message":"No NAT translations found","evidence":"show ip nat translations is empty"})
    return findings

def check_trunk_mismatch(outputs: List[str]) -> List[Dict]:
    findings = []
    trunk_out = [o for o in outputs if "show interfaces trunk" in o.lower()]
    if trunk_out:
        for out in trunk_out:
            if "trunking" not in out.lower() and out.strip().replace("show interfaces trunk","").strip():
                findings.append({"rule_id":"TRUNK_MISMATCH","category":"TRUNK","severity":"HIGH","message":"Trunk port not trunking","evidence":"show interfaces trunk shows no active trunks"})
    return findings

def run_rules(evidence_list) -> List[Dict]:
    outputs = [e.output for e in evidence_list]
    findings = []
    findings.extend(check_duplicate_ips(outputs))
    findings.extend(check_invalid_ips(outputs))
    findings.extend(check_interface_down(outputs))
    findings.extend(check_vlan_missing(outputs))
    findings.extend(check_missing_route(outputs))
    findings.extend(check_acl_deny(outputs))
    findings.extend(check_dhcp_issues(outputs))
    findings.extend(check_nat_issues(outputs))
    findings.extend(check_trunk_mismatch(outputs))
    return findings
