"""Run Chapter 2's deterministic observation perimeter."""

from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS
from orders_investigation.runtime.boundary import ORDERS_BOUNDARY


def main() -> None:
    for task_id, request in sorted(OPENING_OBSERVATION_REQUESTS.items()):
        print(task_id, "permitted" if ORDERS_BOUNDARY.allows(request) else "refused")


if __name__ == "__main__":
    main()

