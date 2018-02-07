import ddt
from django.core.exceptions import ValidationError
from django.test import TestCase

from util.validators import RoleTitleValidator


@ddt.ddt
class TestRoleTitleValidator(TestCase):
	""" Test custom RoleTitleValidator from utils/validators.py"""
	def setUp(self):
		self.validator = RoleTitleValidator()

	@ddt.data(
		'Senior Executive (e.g., CXO, SVP)',
		'Seasoned Leader/Senior Manager (e.g., VP, Director)',
		'Mid-Level Manager (e.g., Manager)',
		'Early Career Professional (e.g., Associate, Analyst)',
		'Other (please describe below)'
	)
	def test_with_valid_input(self, test_text):
		""" With valid input which passes the regex"""
		self.assertIsNone(self.validator(test_text))

	@ddt.data(
		'@#$@%@$#23',
		'Seasoned {Leader/Senior Manager} (e.g., VP, Director)',
		'%Seasoned Leader/Senior Manager (e.g., VP, Director)',
	)
	def test_with_invalid_input(self, test_text):
		"""With in_valid input which doesnt passes the regex"""
		with self.assertRaises(ValidationError):
			self.validator(test_text)
