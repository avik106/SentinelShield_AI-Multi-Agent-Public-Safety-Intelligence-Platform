"""Fraud Graph Intelligence Agent — Local model types."""
from pydantic import BaseModel


class GraphNode(BaseModel):
    node_id: str
    node_type: str    # Person | Phone | UPI | BankAccount | IP | Device | Complaint
    value: str
    properties: dict = {}


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str     # OWNS | CALLED | SHARES_IP | INVOLVES | MENTIONS
