"""Compatibility imports for platform contracts introduced through Chapter 31.

Implementations live in their responsibility subdomains. New code should import the
specific subdomain so the source path teaches the boundary it uses.
"""

from .identity import AgentContract, AgentRegistry
from .capabilities import CapabilityProfile, admit_contract
from .authority import CallerIdentity, Delegation, authorize

__all__ = [
    "AgentContract",
    "AgentRegistry",
    "CapabilityProfile",
    "admit_contract",
    "CallerIdentity",
    "Delegation",
    "authorize"
]
