import pytest
import os
import sys
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, get_db
from app.main import app

# Shared in-memory SQLite with StaticPool so all connections share the same memory DB
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Creates a clean in-memory database for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_case_payload():
    return {
        "title": "Branch Office connectivity loss to Core Switch",
        "symptom": "Host A (192.168.1.50) cannot ping Host B (192.168.2.50) or the default gateway.",
        "topology": {
            "devices": [
                {"name": "Host-A", "type": "host"},
                {"name": "SW-Access-1", "type": "switch"},
                {"name": "R1-Core", "type": "router"}
            ],
            "links": [
                {"source": "Host-A", "source_interface": "eth0", "target": "SW-Access-1", "target_interface": "Gig0/1"},
                {"source": "SW-Access-1", "source_interface": "Gig0/24", "target": "R1-Core", "target_interface": "Gig0/0"}
            ]
        },
        "addressing": [
            {
                "device": "Host-A",
                "interface": "eth0",
                "ip_address": "192.168.1.50",
                "subnet_mask": "255.255.255.0",
                "default_gateway": "192.168.1.1",
                "vlan": 10
            },
            {
                "device": "R1-Core",
                "interface": "Gig0/0.10",
                "ip_address": "192.168.1.1",
                "subnet_mask": "255.255.255.0",
                "default_gateway": None,
                "vlan": 10
            }
        ],
        "show_outputs": {
            "SW-Access-1": {
                "show_interfaces_status": "Gig0/1   connected    10         a-full  a-1000 10/100/1000BaseTX\nGig0/24  connected    trunk      a-full  a-1000 10/100/1000BaseTX",
                "show_vlan_brief": "10   Users                            active    Gig0/1",
                "show_interfaces_trunk": "Gig0/24  10,20,30,40"
            },
            "R1-Core": {
                "show_ip_interface_brief": "Gig0/0.10             192.168.1.1     YES manual up                    up",
                "show_ip_route": "C 192.168.1.0/24 is directly connected, GigabitEthernet0/0.10"
            }
        }
    }
