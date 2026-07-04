"""Engine tests. Real coverage begins in Stage 1."""

import banking


def test_package_importable():
    assert banking.__version__ == "0.1.0"