###############################################################################
#
# Copyright 2020 - Jan Bormet, Anna-Felicitas Hausmann, Joachim Schmidt, Vincent Stollenwerk, Arne Turuc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://www.opensource.org/licenses/mit-license.php
#
###############################################################################


import unittest
from datetime import datetime

from timewsync.file_parser import to_interval_list, to_monthly_data, extract_file_name, extract_tags
from timewsync.interval import Interval


class TestToIntervalList(unittest.TestCase):
    def test_no_data(self):
        self.assertEqual(to_interval_list([]), [])

    def test_single_month(self):
        input_data = ['inc 20201208T133105Z - 20201208T133134Z # 10\ninc 20201208T135322Z # 10']
        expected_intervals = ['inc 20201208T133105Z - 20201208T133134Z # 10', 'inc 20201208T135322Z # 10']
        self.assertEqual(to_interval_list(input_data), expected_intervals)

    def test_multiple_months(self):
        input_data = ['inc 20201213T153500Z - 20201213T161247Z # \"QS1\"\ninc 20201213T153500Z - 20201213T161247Z # QS2',
                      'inc 20210113T153500Z - 20210113T161247Z # QS3']
        expected_intervals = ['inc 20201213T153500Z - 20201213T161247Z # \"QS1\"',
                              'inc 20201213T153500Z - 20201213T161247Z # QS2',
                              'inc 20210113T153500Z - 20210113T161247Z # QS3']
        self.assertEqual(to_interval_list(input_data), expected_intervals)


class TestToMonthlyDate(unittest.TestCase):
    def test_no_intervals(self):
        self.assertEqual(to_monthly_data([]), [])

    def test_single_month(self):
        input_intervals = ['inc 20201208T133105Z - 20201208T133134Z # 10', 'inc 20201208T135322Z # 10']
        expected_data = ['inc 20201208T133105Z - 20201208T133134Z # 10\ninc 20201208T135322Z # 10']
        self.assertEqual(to_monthly_data(input_intervals), expected_data)

    def test_multiple_months(self):
        input_intervals = ['inc 20201213T153500Z - 20201213T161247Z # \"QS1\"',
                           'inc 20201213T153500Z - 20201213T161247Z # QS2',
                           'inc 20210113T153500Z - 20210113T161247Z # QS3']
        expected_data = ['inc 20201213T153500Z - 20201213T161247Z # \"QS1\"\ninc 20201213T153500Z - 20201213T161247Z # QS2',
                         'inc 20210113T153500Z - 20210113T161247Z # QS3']
        self.assertEqual(to_monthly_data(input_intervals), expected_data)


class TestExtractFileName(unittest.TestCase):
    def test_no_entry(self):
        self.assertRaises(AssertionError, extract_file_name, '')

    def test_short_entry(self):
        self.assertEqual(extract_file_name('inc 20200931T235500Z'), '2020-09.data')

    def test_long_entry(self):
        self.assertEqual(extract_file_name('inc 20200931T235500Z - 20201001T000500Z # \"QS\"'), '2020-10.data')

class TestExtractTags(unittest.TestCase):
    def test_no_entry(self):
        self.assertEqual(extract_tags([]), '')

    def test_no_tags(self):
        date1 = datetime(2020, 1, 1)
        date2 = datetime(2021, 5, 29)
        date3 = datetime(2022, 7, 15)
        date4 = datetime(2023, 10, 11)
        i1 = Interval(start=date1, end=date2)
        i2 = Interval(start=date2, end=date3)
        i3 = Interval(start=date3, end=date4)
        self.assertEqual(extract_tags([i1, i2, i3]), '')

    def test_mixed_input(self):
        date1 = datetime(2020, 1, 1)
        date2 = datetime(2021, 5, 29)
        date3 = datetime(2022, 7, 15)
        date4 = datetime(2023, 10, 11)
        i1 = Interval(start=date1, end=date2)
        i2 = Interval(start=date2, end=date3, tags = ["tag1", "tag2", "tag3", "tag4", "tag1"])
        i3 = Interval(start=date3, end=date4, tags = ["tag2"], annotation="I am the annotation.")
        i4 = Interval(start=date1, end=date3, tags = ["tag3", "tag2"], annotation= "I am another annotation.")
        i5 = Interval(start=date3, end=date4, annotation= "I am the third annotation.")
        self.assertEqual(extract_tags([i1, i2, i3, i4, i5]), '{"tag1":{"count":2},"tag2":{"count":3},"tag3":{"count":2},"tag4":{"count":1}}')
