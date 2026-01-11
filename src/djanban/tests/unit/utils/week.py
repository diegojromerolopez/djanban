
# -*- coding: utf-8 -*-
import unittest
from datetime import date, timedelta
from mock import patch
from djanban.utils.week import *

class TestWeek(unittest.TestCase):
    def test_get_iso_week_of_year(self):
        d = date(2023, 1, 1) # This is a Sunday
        # In ISO calendar, 2023-01-01 is part of week 52 of 2022
        self.assertEqual(get_iso_week_of_year(d), 52)
        
        d2 = date(2023, 1, 2) # This is a Monday
        self.assertEqual(get_iso_week_of_year(d2), 1)

    @patch('django.utils.timezone.now')
    def test_get_iso_week_of_year_none(self, mock_now):
        mock_now.return_value.date.return_value = date(2023, 1, 2)
        self.assertEqual(get_iso_week_of_year(None), 1)

    def test_get_week_of_year(self):
        d = date(2023, 1, 2)
        self.assertEqual(get_week_of_year(d), u"2023W1")

    @patch('django.utils.timezone.now')
    def test_get_week_of_year_none(self, mock_now):
        mock_now.return_value.date.return_value = date(2023, 1, 2)
        self.assertEqual(get_week_of_year(None), u"2023W1")

    def test_get_weeks_of_year_since_one_year_ago(self):
        d = date(2023, 1, 2)
        weeks = get_weeks_of_year_since_one_year_ago(d)
        self.assertEqual(len(weeks), 53)
        self.assertEqual(weeks[0], u"2023W1")
        self.assertEqual(weeks[1], u"2022W52")

    @patch('django.utils.timezone.now')
    def test_get_weeks_of_year_since_one_year_ago_none(self, mock_now):
        mock_now.return_value.date.return_value = date(2023, 1, 2)
        weeks = get_weeks_of_year_since_one_year_ago(None)
        self.assertEqual(len(weeks), 53)
        self.assertEqual(weeks[0], u"2023W1")

    def test_number_of_weeks_of_year(self):
        self.assertEqual(number_of_weeks_of_year(2023), 52)

    def test_start_of_week_of_year(self):
        # 2023W1 starts on 2023-01-02 (Monday)
        self.assertEqual(start_of_week_of_year(1, 2023), date(2023, 1, 2))

    def test_end_of_week_of_year(self):
        # 2023W1 ends on 2023-01-08 (Sunday)
        self.assertEqual(end_of_week_of_year(1, 2023), date(2023, 1, 8))
