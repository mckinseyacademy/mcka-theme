import ddt
from django.test import TestCase

from util.math_helpers import round_to_int, round_to_int_bump_zero, calculate_percentage


@ddt.ddt
class TestMathHelpers(TestCase):
    """Test cases for testing math helper round_to_int_bump_zero """

    @ddt.unpack
    @ddt.data(
        (0.1, 1),
        (0.999, 1),
        (0, 0),
        (0.0001, 1),
        (12.1232, 12),
        (12.67, 13),
    )
    def test_round_to_int_bump_zero(self, number, expected_result):
        """With number and expected results"""
        self.assertEqual(round_to_int_bump_zero(number), expected_result)

    @ddt.unpack
    @ddt.data(
        (12, 12),
        (12.1232, 12),
        (12.67, 13),
    )
    def test_round_to_int(self, number, expected_result):
        """Testing round_to_int with various inputs"""
        self.assertEqual(round_to_int(number), expected_result)

    @ddt.unpack
    @ddt.data(
        (12, 12, 100),
        (12, 6, 200),
        (0, 13, 0),
        (0.01, 100, 1),
    )
    def test_percentage(self, part, whole, expected_result):
        self.assertEqual(calculate_percentage(part, whole), expected_result)
