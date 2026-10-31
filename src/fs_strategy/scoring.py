"""Dynamic discipline scoring from Formula Student Rules 2026 v1.1 D9.1.1."""

from __future__ import annotations

from typing import Any


def score_d9_default(
    time_s: float,
    tmin_s: float,
    pmax: float,
    pmin: float,
    tmax_s: float,
    *,
    has_valid_run: bool,
) -> float:
    """Apply the D9.1.1 default scoring formula (FS Rules 2026 v1.1).

    SCORE = (Pmax - Pmin) * ((Tmax - Tteam) / (Tmax - Tmin))**2 + Pmin

    Tteam is the team's best time including penalties, capped at Tmax (D9.1.1).
    Pmin and Tmax come from Table 11 via the competition YAML, not from code.
    A team with no valid run scores 0 (D1.1.5 treats DNF as DQ; D1.1.9 requires
    a valid run to score points).
    """
    if tmin_s <= 0:
        raise ValueError(f"Minimum time must be positive, got {tmin_s} s")
    if not has_valid_run:
        return 0.0
    if time_s < tmin_s:
        raise ValueError(
            f"Team time {time_s} s is faster than the field minimum {tmin_s} s"
        )

    tteam_s = min(time_s, tmax_s)
    return (pmax - pmin) * ((tmax_s - tteam_s) / (tmax_s - tmin_s)) ** 2 + pmin


def _discipline_points(
    time_s: float,
    tmin_s: float,
    has_valid_run: bool,
    config: dict[str, Any],
    discipline: str,
) -> float:
    params = config["disciplines"][discipline]
    pmax = float(config["max_points"][discipline])
    pmin = params["pmin_fraction"] * pmax
    tmax_s = params["tmax_multiplier"] * tmin_s
    return score_d9_default(
        time_s,
        tmin_s,
        pmax,
        pmin,
        tmax_s,
        has_valid_run=has_valid_run,
    )


def score_acceleration(
    time_s: float,
    tmin_s: float,
    has_valid_run: bool,
    config: dict[str, Any],
) -> float:
    """Acceleration points using D9.1.1 and Table 11 (FS Rules 2026 v1.1).

    ``time_s`` is the already-built run time (best valid run including penalties).
    ``tmax_multiplier`` and ``pmin_fraction`` are read from ``config``.
    """
    return _discipline_points(time_s, tmin_s, has_valid_run, config, "acceleration")


def score_skidpad(
    time_s: float,
    tmin_s: float,
    has_valid_run: bool,
    config: dict[str, Any],
) -> float:
    """Skidpad points using D9.1.1 and Table 11 (FS Rules 2026 v1.1).

    ``time_s`` is the already-built run time. Combining left/right circles and
    adding cone penalties after averaging (D4.2.2) is out of scope here.
    """
    return _discipline_points(time_s, tmin_s, has_valid_run, config, "skidpad")
