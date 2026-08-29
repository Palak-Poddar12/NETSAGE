# NetSage AI Backend

Backend service for NetSage AI, an AI-assisted Cisco network troubleshooting system for Packet Tracer labs.

## Architecture

Packet Tracer → FastAPI Backend → Validation → Rule Engine → AI Diagnosis → Evidence Correlation → Human Review → SQLite → Dashboard API

## Installation

Create and activate a Python 3.11+ virtual environment:

```bash
python -m venv .venv
