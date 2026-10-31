"""Load and validate competition YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED_TOP_LEVEL = (
    "event_id",
    "class",
    "year",
    "rules_year",
    "verification",
    "source",
    "max_points",
    "disciplines",
)

REQUIRED_DISCIPLINES = ("skidpad", "acceleration")
REQUIRED_DISCIPLINE_FIELDS = ("tmax_multiplier", "pmin_fraction")


def load_competition_config(path: str | Path) -> dict[str, Any]:
    """Load a competition YAML file and check required fields and numeric bounds.

    Raises:
        ValueError: missing fields, negative maximum points, tmax_multiplier <= 1,
            or pmin_fraction outside [0, 1).
    """
    config_path = Path(path)
    with config_path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    if not isinstance(loaded, dict):
        raise ValueError(f"Competition config must be a mapping: {config_path}")

    missing = [name for name in REQUIRED_TOP_LEVEL if name not in loaded]
    if missing:
        raise ValueError(
            f"Competition config {config_path} is missing fields: {', '.join(missing)}"
        )

    max_points = loaded["max_points"]
    if not isinstance(max_points, dict) or not max_points:
        raise ValueError(f"max_points must be a non-empty mapping: {config_path}")

    for discipline_name, points in max_points.items():
        if points is None or points < 0:
            raise ValueError(
                f"Maximum points for {discipline_name} must be non-negative, got {points}"
            )

    disciplines = loaded["disciplines"]
    if not isinstance(disciplines, dict):
        raise ValueError(f"disciplines must be a mapping: {config_path}")

    missing_disciplines = [name for name in REQUIRED_DISCIPLINES if name not in disciplines]
    if missing_disciplines:
        raise ValueError(
            "Competition config "
            f"{config_path} is missing disciplines: {', '.join(missing_disciplines)}"
        )

    for discipline_name, params in disciplines.items():
        if not isinstance(params, dict):
            raise ValueError(f"Discipline {discipline_name} must be a mapping")
        missing_params = [name for name in REQUIRED_DISCIPLINE_FIELDS if name not in params]
        if missing_params:
            raise ValueError(
                f"Discipline {discipline_name} is missing fields: {', '.join(missing_params)}"
            )

        tmax_multiplier = params["tmax_multiplier"]
        pmin_fraction = params["pmin_fraction"]
        if tmax_multiplier <= 1:
            raise ValueError(
                f"tmax_multiplier for {discipline_name} must be > 1, got {tmax_multiplier}"
            )
        if not 0 <= pmin_fraction < 1:
            raise ValueError(
                "pmin_fraction for "
                f"{discipline_name} must satisfy 0 <= pmin_fraction < 1, got {pmin_fraction}"
            )

    return loaded
