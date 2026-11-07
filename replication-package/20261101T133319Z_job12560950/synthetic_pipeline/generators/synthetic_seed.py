"""Single public perturbation control shared by every Stage-B generator."""
import os


ENV_NAME = "FDA_SYNTHETIC_SEED_OFFSET"


def seed(base):
    raw = os.environ.get(ENV_NAME, "0")
    try:
        offset = int(raw)
    except ValueError as exc:
        raise SystemExit(f"{ENV_NAME} must be an integer, got {raw!r}") from exc
    value = int(base) + offset
    if value < 0 or value >= 2**63:
        raise SystemExit(f"{ENV_NAME} produces an invalid seed: {value}")
    return value
