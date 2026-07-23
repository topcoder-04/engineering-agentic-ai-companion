"""Compatibility imports for platform contracts introduced through Chapter 29.

Implementations live in their responsibility subdomains. New code should import the
specific subdomain so the source path teaches the boundary it uses.
"""

from .identity import AgentContract, AgentRegistry

__all__ = [
    "AgentContract",
    "AgentRegistry"
]
