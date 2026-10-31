"""Minimal import check for the installed package."""

import numpy


def test_numpy_import_and_addition() -> None:
    assert numpy is not None
    assert 1 + 1 == 2
