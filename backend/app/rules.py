import ipaddress
import re
from collections import defaultdict
from typing import Any


SUPPORTED_COMMANDS = {
    "show ip interface brief",
    "show running-config",
    "show vlan brief",
    "show interfaces trunk",
    "show ip route",
    "show access-lists",
    "show ip nat translations",
    "show ip dhcp binding",
}

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def _finding(rule_id: str, category: str, severity: str, message: str, evidence: str) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "message": message,
        "evidence": evidence,
    }


def _valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _extract_ipv4_tokens(text: str) -> list[str]:
    return re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)


def _parse_addressing(addressing: str) -> list[tuple[str, str, str | None]]:
    records = []
    for line in addressing.splitlines():
        ips = _extract_ipv4_tokens(line)
        if not ips:
            continue
        label = line.split(":", 1)[0].strip() if ":" in line else "addressing"
        ip = ips[0]
        mask = ips[1] if len(ips) > 1 else None
        records.append((label, ip, mask))
    return records


def run_rules(case: Any, evidence: list[Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    all_text = "\n".join(e.output for e in evidence)
    commands = {e.command.strip().lower() for e in evidence}

    # Invalid addresses in supplied case/addressing information.
    for label, ip, mask in _parse_addressing(case.addressing):
        if not _valid_ip(ip):
            findings.append(_finding(
                "INVALID_IP",
                "IP_ADDRESSING",
                "HIGH",
                f"Invalid IP address supplied for {label}: {ip}",
                case.addressing,
            ))
        if mask and not _valid_ip(mask):
            try:
                ipaddress.IPv4Network(f"0.0.0.0/{mask}")
            except ValueError:
                findings.append(_finding(
                    "INVALID_MASK",
                    "SUBNET",
                    "HIGH",
                    f"Invalid subnet mask supplied for {label}: {mask}",
                    case.addressing,
                ))

    # Duplicate IPv4 addresses can be established when the addressing text
    # explicitly associates the same address with multiple labelled records.
    address_owners: dict[str, list[str]] = defaultdict(list)
    for label, ip, _ in _parse_addressing(case.addressing):
        if _valid_ip(ip):
            address_owners[ip].append(label)
    for ip, owners in address_owners.items():
        if len(set(owners)) > 1:
            findings.append(_finding(
                "DUPLICATE_IP",
                "IP_ADDRESSING",
                "CRITICAL",
                f"IP address {ip} is assigned to multiple supplied records.",
                case.addressing,
            ))

    # Interface status.
    if "show ip interface brief" in commands:
        for line in all_text.splitlines():
            match = re.search(
                r"^(\S+)\s+((?:\d{1,3}\.){3}\d{1,3}|unassigned)\s+\S+\s+\S+\s+(\S+)\s+(\S+)",
                line.strip(),
                re.IGNORECASE,
            )
            if match:
                interface, _, status, protocol = match.groups()
                if status.lower() == "administratively down":
                    findings.append(_finding(
                        "INTERFACE_ADMIN_DOWN",
                        "INTERFACE",
                        "HIGH",
                        f"Interface {interface} is administratively down.",
                        line.strip(),
                    ))
                elif status.lower() == "down" and protocol.lower() == "down":
                    findings.append(_finding(
                        "INTERFACE_OPERATIONAL_DOWN",
                        "INTERFACE",
                        "HIGH",
                        f"Interface {interface} is operationally down.",
                        line.strip(),
                    ))

    # VLAN existence and access/trunk evidence.
    vlan_ids = set(re.findall(r"(?m)^\s*(\d+)\s+\S+", "\n".join(
        e.output for e in evidence if e.command.strip().lower() == "show vlan brief"
    )))
    access_mismatches = re.findall(
        r"(?i)(?:access vlan|access vlan is)\s+(\d+).{0,80}(?:expected|required)\s+vlan\s+(\d+)",
        all_text,
    )
    for actual, expected in access_mismatches:
        if actual != expected:
            findings.append(_finding(
                "ACCESS_VLAN_MISMATCH",
                "VLAN",
                "HIGH",
                f"Access VLAN {actual} does not match expected VLAN {expected}.",
                f"actual={actual}, expected={expected}",
            ))

    missing_vlan_matches = re.findall(
        r"(?i)(?:missing|requires|required)\s+vlan\s+(\d+)",
        case.topology + "\n" + case.addressing + "\n" + case.symptom,
    )
    for vlan in set(missing_vlan_matches):
        if "show vlan brief" in commands and vlan not in vlan_ids:
            findings.append(_finding(
                "VLAN_MISSING",
                "VLAN",
                "HIGH",
                f"VLAN {vlan} is missing.",
                f"show vlan brief does not contain VLAN {vlan}",
            ))

    # Trunk allowed VLAN mismatch when output contains explicit allowed lists.
    trunk_lines = [
        e.output for e in evidence
        if e.command.strip().lower() == "show interfaces trunk"
    ]
    for output in trunk_lines:
        for line in output.splitlines():
            if re.search(r"(?i)allowed.*vlan.*active", line):
                continue
            match = re.search(r"(?i)allowed.*?vlan(?:s)?\s*[: ]\s*([0-9,\- ]+)", line)
            if match and re.search(r"(?i)required|expected", case.topology + "\n" + case.addressing):
                expected = re.findall(r"(?i)(?:required|expected).*?vlan(?:s)?\s*[: ]\s*([0-9,\- ]+)", case.topology + "\n" + case.addressing)
                if expected and expected[0].strip() != match.group(1).strip():
                    findings.append(_finding(
                        "TRUNK_VLAN_MISMATCH",
                        "TRUNK",
                        "HIGH",
                        "Supplied trunk VLAN list does not match the stated expected VLAN list.",
                        line.strip(),
                    ))

    # Routes.
    route_outputs = [
        e.output for e in evidence
        if e.command.strip().lower() == "show ip route"
    ]
    if route_outputs:
        route_text = "\n".join(route_outputs)
        if re.search(r"(?m)^\s*[Cc]\s+", route_text) is None and re.search(r"(?i)connected", route_text) is None:
            pass
        stated_networks = re.findall(
            r"(?i)(?:route to|network|subnet)\s+((?:\d{1,3}\.){3}\d{1,3}/\d{1,2})",
            case.symptom + "\n" + case.topology + "\n" + case.addressing,
        )
        for network in stated_networks:
            try:
                target = ipaddress.ip_network(network, strict=False)
            except ValueError:
                continue
            if not any(str(target.network_address) in output for output in route_outputs):
                findings.append(_finding(
                    "MISSING_ROUTE",
                    "ROUTING",
                    "HIGH",
                    f"No supplied route evidence was found for {network}.",
                    "show ip route does not contain the stated network.",
                ))

        if re.search(r"(?m)^\s*(?:S\*|S\*E2|O\*E2).*(?:0\.0\.0\.0/0|Gateway of last resort)", route_text) is None:
            if re.search(r"(?i)(?:internet|default route|default gateway)", case.symptom + "\n" + case.topology):
                findings.append(_finding(
                    "MISSING_DEFAULT_ROUTE",
                    "ROUTING",
                    "HIGH",
                    "The supplied routing evidence does not show a default route.",
                    "show ip route contains no visible default-route entry.",
                ))

    # Basic ACL deny.
    if "show access-lists" in commands:
        acl_outputs = "\n".join(
            e.output for e in evidence
            if e.command.strip().lower() == "show access-lists"
        )
        if re.search(r"(?i)\bdeny\b", acl_outputs):
            findings.append(_finding(
                "ACL_DENY",
                "ACL",
                "HIGH",
                "A deny entry is present in the supplied ACL output.",
                re.search(r"(?i)^.*\bdeny\b.*$", acl_outputs, re.MULTILINE).group(0).strip()
                if re.search(r"(?i)^.*\bdeny\b.*$", acl_outputs, re.MULTILINE)
                else "show access-lists contains a deny entry",
            ))

    # Basic DHCP evidence.
    if "show ip dhcp binding" in commands:
        dhcp_output = "\n".join(
            e.output for e in evidence
            if e.command.strip().lower() == "show ip dhcp binding"
        )
        if not dhcp_output.strip() or re.search(r"(?i)(no bindings|none|empty)", dhcp_output):
            findings.append(_finding(
                "DHCP_NO_BINDING",
                "DHCP",
                "MEDIUM",
                "The supplied DHCP binding output contains no active bindings.",
                dhcp_output.strip() or "show ip dhcp binding returned empty output",
            ))

    # Basic DNS evidence: only report an issue when explicit DNS configuration
    # is stated but no nameserver evidence is present in supplied configuration.
    if "show running-config" in commands and re.search(r"(?i)\bdns\b|\bnameserver\b", case.symptom + "\n" + case.addressing):
        running = "\n".join(
            e.output for e in evidence
            if e.command.strip().lower() == "show running-config"
        )
        if not re.search(r"(?i)(ip name-server|nameserver)\s+\S+", running):
            findings.append(_finding(
                "DNS_CONFIG_MISSING",
                "DNS",
                "MEDIUM",
                "DNS is relevant to the supplied case, but no nameserver configuration is visible.",
                "show running-config contains no visible ip name-server entry.",
            ))

    # Basic NAT evidence.
    if "show ip nat translations" in commands:
        nat_output = "\n".join(
            e.output for e in evidence
            if e.command.strip().lower() == "show ip nat translations"
        )
        if re.search(r"(?i)(no translations|none|empty)", nat_output) or not nat_output.strip():
            if re.search(r"(?i)\bnat\b", case.symptom + "\n" + case.topology):
                findings.append(_finding(
                    "NAT_NO_TRANSLATION",
                    "NAT",
                    "MEDIUM",
                    "NAT is relevant to the supplied case, but no translation is visible.",
                    nat_output.strip() or "show ip nat translations returned empty output",
                ))

    # Gateway checks from explicit "gateway" records in addressing.
    for line in case.addressing.splitlines():
        if re.search(r"(?i)\bgateway\b", line):
            ips = _extract_ipv4_tokens(line)
            if not ips:
                continue
            gateway = ips[-1]
            if not _valid_ip(gateway):
                continue
            preceding_ips = _extract_ipv4_tokens(case.addressing.replace(line, ""))
            if preceding_ips:
                host_ip = preceding_ips[0]
                masks = re.findall(r"/(\d{1,2})\b", line)
                if masks:
                    try:
                        network = ipaddress.ip_network(f"{host_ip}/{masks[0]}", strict=False)
                        if ipaddress.ip_address(gateway) not in network:
                            findings.append(_finding(
                                "GATEWAY_OUTSIDE_SUBNET",
                                "GATEWAY",
                                "HIGH",
                                f"Gateway {gateway} is outside subnet {network}.",
                                line.strip(),
                            ))
                    except ValueError:
                        pass

    return findings


def validate_command(command: str) -> str:
    normalized = " ".join(command.strip().lower().split())
    if normalized not in SUPPORTED_COMMANDS:
        raise ValueError(
            f"Unsupported command. Supported commands: {', '.join(sorted(SUPPORTED_COMMANDS))}"
        )
    return normalized


def severity_of(findings: list[dict[str, str]]) -> str:
    if not findings:
        return "NONE"
    return max(findings, key=lambda item: SEVERITY_ORDER.get(item["severity"], 0))["severity"]
