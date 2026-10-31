"""Tests for competition YAML loading and validation."""

from pathlib import Path

import pytest
import yaml

from fs_strategy.data_io import load_competition_config

REPO_ROOT = Path(__file__).resolve().parents[1]
FSG_2026 = REPO_ROOT / "config" / "competitions" / "fsg_2026_cv.yaml"
FSS_2026 = REPO_ROOT / "config" / "competitions" / "fss_2026_cv.yaml"


def test_load_official_fsg_config() -> None:
    config = load_competition_config(FSG_2026)
    assert config["verification"] == "official"
    assert config["max_points"]["skidpad"] == 50
    assert config["max_points"]["acceleration"] == 50
    assert config["disciplines"]["skidpad"]["tmax_multiplier"] == 1.35
    assert config["disciplines"]["acceleration"]["tmax_multiplier"] == 1.7


def test_load_fss_config_marked_to_verify() -> None:
    config = load_competition_config(FSS_2026)
    assert config["verification"] == "to_verify"
    assert config["max_points"]["skidpad"] == 75
    assert config["max_points"]["acceleration"] == 75


def test_missing_field_raises(tmp_path: Path) -> None:
    payload = yaml.safe_load(FSG_2026.read_text(encoding="utf-8"))
    del payload["event_id"]
    broken = tmp_path / "missing.yaml"
    broken.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="missing fields: event_id"):
        load_competition_config(broken)


def test_negative_points_raises(tmp_path: Path) -> None:
    payload = yaml.safe_load(FSG_2026.read_text(encoding="utf-8"))
    payload["max_points"]["acceleration"] = -1
    broken = tmp_path / "negative.yaml"
    broken.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="non-negative"):
        load_competition_config(broken)


def test_tmax_multiplier_not_greater_than_one_raises(tmp_path: Path) -> None:
    payload = yaml.safe_load(FSG_2026.read_text(encoding="utf-8"))
    payload["disciplines"]["acceleration"]["tmax_multiplier"] = 1.0
    broken = tmp_path / "tmax.yaml"
    broken.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="tmax_multiplier"):
        load_competition_config(broken)
