"""Run Chapter 18's responsibility boundary from its real package."""

import importlib


def main() -> None:
    boundary = importlib.import_module("orders_investigation.governance.approval")
    public = sorted(name for name in vars(boundary) if not name.startswith("_"))
    print("CHAPTER 18 BOUNDARY")
    print("module:", boundary.__name__)
    print("public contracts:", ", ".join(public))
    print("The cumulative tests execute this boundary's success and refusal paths.")


if __name__ == "__main__":
    main()


