from datetime import date

from django.test import TestCase

from .utils import sanitize_month


# Create your tests here.
class UtilsTests(TestCase):
    def test_sanitize_month(self):
        self.assertEqual(sanitize_month(0), date.today().month)
        self.assertEqual(sanitize_month("0"), date.today().month)
        self.assertEqual(sanitize_month("13"), date.today().month)
        self.assertEqual(sanitize_month("bogus"), date.today().month)
        self.assertEqual(sanitize_month(None), date.today().month)
        self.assertEqual(sanitize_month(13), date.today().month)
        self.assertEqual(sanitize_month(-1), date.today().month)
        self.assertEqual(sanitize_month(1), 1)
        self.assertEqual(sanitize_month("1"), 1)
        self.assertEqual(sanitize_month(12), 12)
        self.assertEqual(sanitize_month(5), 5)
