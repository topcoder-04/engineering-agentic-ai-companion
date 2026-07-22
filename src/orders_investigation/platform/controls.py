"""Compatibility imports for platform contracts introduced through Chapter 37.

Implementations live in their responsibility subdomains. New code should import the
specific subdomain so the source path teaches the boundary it uses.
"""

from .identity import AgentContract, AgentRegistry
from .capabilities import CapabilityProfile, admit_contract
from .authority import CallerIdentity, Delegation, authorize
from .placement import DataBoundary, ExecutionTarget, place
from .defaults import Scaffold, ScaffoldRequest, scaffold
from .releases import ConformanceReceipt, release_conforms
from .lifecycle import ExceptionGrant, validate_exception
from .compatibility import CompatibilityWindow, migration_step
from .risk import LaunchEvidence, RiskTier, approve_launch

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
    "place",
    "Scaffold",
    "ScaffoldRequest",
    "scaffold",
    "ConformanceReceipt",
    "release_conforms",
    "ExceptionGrant",
    "validate_exception",
    "CompatibilityWindow",
    "migration_step",
    "LaunchEvidence",
    "RiskTier",
    "approve_launch"
]
