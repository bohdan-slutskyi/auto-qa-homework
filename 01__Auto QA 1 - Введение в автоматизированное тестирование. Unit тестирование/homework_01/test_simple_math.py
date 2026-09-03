import pytest

from simple_math import SimpleMath


@pytest.fixture
def simple_math():
    return SimpleMath()


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (2, 4),
        (-3, 9),
        (0, 0),
    ],
)
def test_square(simple_math, number, expected):
    assert simple_math.square(number) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (2, 8),
        (-3, -27),
        (0, 0),
    ],
)
def test_cube(simple_math, number, expected):
    assert simple_math.cube(number) == expected
