from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    operation: str
    source: str
    environment: str
    resource: str
    detail: str


@dataclass(frozen=True)
class InvestigationBoundary:
    environment: str
    readable_sources: frozenset[str]
    writable_resource: str

    def allows(self, request: Request) -> bool:
        if request.environment != self.environment:
            return False
        if request.operation == "observe":
            return request.source in self.readable_sources
        if request.operation == "update_report":
            return (
                request.source == "incident_record"
                and request.resource == self.writable_resource
            )
        return False


ORDERS_BOUNDARY = InvestigationBoundary(
    environment="orders-production",
    readable_sources=frozenset(
        {
            "service_metrics",
            "database_monitoring",
            "migration_records",
            "deployment_records",
        }
    ),
    writable_resource="incident_report",
)
