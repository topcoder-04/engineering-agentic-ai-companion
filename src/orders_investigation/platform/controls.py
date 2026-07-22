"""Compatibility imports for platform contracts introduced through Chapter 32.

Implementations live in their responsibility subdomains. New code should import the
specific subdomain so the source path teaches the boundary it uses.
"""

from .identity import AgentContract, AgentRegistry
from .capabilities import CapabilityProfile, admit_contract
from .authority import CallerIdentity, Delegation, authorize
from .placement import DataBoundary, ExecutionTarget, place

__all__ = [
    "AgentContract",
    "AgentRegistry",
    "CapabilityProfile",
    "admit_contract",
    "CallerIdentity",
    "Delegation",
    "authorize",
    "DataBoundary",
    "ExecutionTarget",
    "place"
]
