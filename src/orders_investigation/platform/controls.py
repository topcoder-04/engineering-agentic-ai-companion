"""Compatibility imports for platform contracts introduced through Chapter 30.

Implementations live in their responsibility subdomains. New code should import the
specific subdomain so the source path teaches the boundary it uses.
"""

from .identity import AgentContract, AgentRegistry
from .capabilities import CapabilityProfile, admit_contract

__all__ = [
    "AgentContract",
    "AgentRegistry",
    "CapabilityProfile",
    "admit_contract"
]
