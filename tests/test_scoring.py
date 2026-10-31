"""Hand-checked D9.1.1 scoring cases (FS Rules 2026 v1.1)."""

from pathlib import Path

import pytest

from fs_strategy.data_io import load_competition_config
from fs_strategy.scoring import score_acceleration, score_skidpad

REPO_ROOT = Path(__file__).resolve().parents[1]
FSG = load_competition_config(REPO_ROOT / "config" / "competitions" / "fsg_2026_cv.yaml")
FSS = load_competition_config(REPO_ROOT / "config" / "competitions" / "fss_2026_cv.yaml")


def test_fss_acceleration_fastest_gets_pmax() -> None:
    # Pmax=75, Pmin=0.05*75=3.75, Tmin=4.0, Tmax=1.7*4.0=6.8
    # Tteam=Tmin => ratio=1 => SCORE=75
    assert score_acceleration(4.0, 4.0, True, FSS) == pytest.approx(75.0)


def test_fss_acceleration_midfield() -> None:
    # (75-3.75)*((6.8-5.0)/(6.8-4.0))**2 + 3.75
    # = 71.25 * (1.8/2.8)**2 + 3.75 = 71.25 * 81/196 + 3.75 ≈ 33.195
    assert score_acceleration(5.0, 4.0, True, FSS) == pytest.approx(33.195, abs=1e-3)


def test_fss_acceleration_at_tmax_scores_pmin() -> None:
    # Tteam=Tmax=6.8 => SCORE=Pmin=3.75
    assert score_acceleration(6.8, 4.0, True, FSS) == pytest.approx(3.75)


def test_fss_acceleration_slower_than_tmax_still_pmin() -> None:
    # Valid run, Tteam capped at Tmax, not zero (D9.1.1 cap)
    assert score_acceleration(7.5, 4.0, True, FSS) == pytest.approx(3.75)


def test_no_valid_run_scores_zero() -> None:
    # D1.1.5 DNF treated as DQ; D1.1.9 no valid run => 0 points
    assert score_acceleration(4.0, 4.0, False, FSS) == pytest.approx(0.0)
    assert score_skidpad(5.0, 5.0, False, FSG) == pytest.approx(0.0)


def test_fsg_acceleration_midfield() -> None:
    # Pmax=50, Pmin=2.5, Tmin=4.0, Tmax=6.8, Tteam=5.0
    # 47.5 * (1.8/2.8)**2 + 2.5 = 47.5 * 81/196 + 2.5 ≈ 22.130
    assert score_acceleration(5.0, 4.0, True, FSG) == pytest.approx(22.130, abs=1e-3)


def test_fsg_skidpad_midfield() -> None:
    # Pmax=50, Pmin=2.5, Tmin=5.0, Tmax=1.35*5.0=6.75, Tteam=5.5
    # 47.5 * ((6.75-5.5)/(6.75-5.0))**2 + 2.5
    # = 47.5 * (1.25/1.75)**2 + 2.5 = 47.5 * 25/49 + 2.5 ≈ 26.735
    assert score_skidpad(5.5, 5.0, True, FSG) == pytest.approx(26.735, abs=1e-3)


def test_slower_valid_time_never_scores_more() -> None:
    times_s = [4.0, 4.5, 5.0, 6.0, 6.8, 8.0]
    scores = [score_acceleration(time_s, 4.0, True, FSS) for time_s in times_s]
    assert scores == sorted(scores, reverse=True)


def test_non_positive_tmin_raises() -> None:
    with pytest.raises(ValueError, match="positive"):
        score_acceleration(4.0, 0.0, True, FSS)


def test_team_faster_than_tmin_raises() -> None:
    with pytest.raises(ValueError, match="faster than the field minimum"):
        score_acceleration(3.9, 4.0, True, FSS)
