from datetime import date

from django.test import TestCase

from .utils import sanitize_month, sanitize_year


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

    def test_sanitize_year(self):
        self.assertEqual(sanitize_year(0), date.today().year)
        self.assertEqual(sanitize_year("0"), date.today().year)
        self.assertEqual(sanitize_year("bogus"), date.today().year)
        self.assertEqual(sanitize_year(None), date.today().year)
        self.assertEqual(sanitize_year(-1), date.today().year)
        self.assertEqual(sanitize_year(1), 1)
        self.assertEqual(sanitize_year("1"), 1)
        self.assertEqual(sanitize_year(12), 12)
        self.assertEqual(sanitize_year(5), 5)
        self.assertEqual(sanitize_year(2015), 2015)
