# NetSage AI 🌐🤖

### AI-Assisted Cisco Packet Tracer Troubleshooting & Network Diagnosis Platform

NetSage AI is an AI-assisted network troubleshooting platform designed to help students, network engineers, and administrators diagnose Cisco networking problems using a combination of **deterministic Python network rules, AI reasoning, evidence correlation, and human review**.

The system accepts a network symptom, topology information, IP addressing details, and Cisco `show` command outputs. It first performs deterministic network checks and then uses an LLM to generate an evidence-based diagnosis.

> ⚠️ **NetSage AI is an assistant, not an autonomous network configurator.**
> It can recommend commands and fixes, but it never automatically modifies a network.

---

## 🚀 Why NetSage AI?

Traditional AI chatbots can provide networking answers, but they may:

- Guess the root cause
- Hallucinate network configurations
- Invent command outputs
- Ignore conflicting evidence
- Recommend fixes without sufficient evidence

NetSage AI follows an **Evidence First → AI Second → Human Approval** approach.

```text
Network Evidence
       ↓
Input Validation
       ↓
Deterministic Rule Engine
       ↓
AI Diagnosis
       ↓
Evidence Correlation
       ↓
AI Evaluation
       ↓
Human Review
       ↓
Audit Trail
       ↓
Dashboard
