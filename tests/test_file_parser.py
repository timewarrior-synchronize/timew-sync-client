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


from datetime import datetime

import pytest

from timewsync.file_parser import (
    to_interval_list,
    to_monthly_data,
    get_file_name,
    extract_tags,
)
from timewsync.interval import Interval


class TestToIntervalList:
    def test_no_data(self):
        """Tests with no intervals in list."""
        assert to_interval_list([]) == []
        assert to_interval_list([""]) == []
        assert to_interval_list(["\n\n"]) == []

    def test_with_data(self):
        """Tests intervals starting in the same/different months."""
        test_date1 = "20210123T134659Z"
        test_date2 = "20210124T020043Z"
        test_date3 = "20210201T134501Z"
        test_date4 = "20210301T145012Z"
        test_tags = 'shortTag "tag - with quotes" "\\nt3$T "edg€ case! " \\""'
        test_annotation = "this interval is for testing purposes only"

        test_interval_str1 = (
            "inc "
            + test_date1
            + " - "
            + test_date2
            + " # "
            + test_tags
            + " # "
            + test_annotation
        )
        test_interval_str2 = "inc " + test_date1 + " - " + test_date2
        test_interval_str3 = (
            "inc " + test_date3 + " - " + test_date4 + " # # " + "foo bar"
        )

        expt_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
        expt_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        expt_date3 = datetime.fromisoformat("2021-02-01 13:45:01")
        expt_date4 = datetime.fromisoformat("2021-03-01 14:50:12")
        expt_tags = [
            "shortTag",
            '"tag - with quotes"',
            '"\\nt3$T "edg€ case! "',
            '\\""',
        ]
        expt_annotation = "this interval is for testing purposes only"

        expt_interval1 = Interval(
            start=expt_date1, end=expt_date2, tags=expt_tags, annotation=expt_annotation
        )
        expt_interval2 = Interval(start=expt_date1, end=expt_date2)
        expt_interval3 = Interval(
            start=expt_date3, end=expt_date4, annotation="foo bar"
        )

        # Test with similar intervals
        test_intervals = to_interval_list(
            [test_interval_str1 + "\n" + test_interval_str2]
        )
        expt_intervals = [expt_interval1, expt_interval2]
        assert test_intervals == expt_intervals

        # Test with multiple months
        test_intervals = to_interval_list(
            [test_interval_str1 + "\n" + test_interval_str2, test_interval_str3]
        )
        expt_intervals = [expt_interval1, expt_interval2, expt_interval3]
        assert test_intervals == expt_intervals


class TestToMonthlyData:
    def test_no_intervals(self):
        """Tests with no intervals in list."""
        assert to_monthly_data([]) == {}

    def test_with_intervals(self):
        """Tests un-/sorted intervals starting in the same/different months."""
        test_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
        test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        test_date3 = datetime.fromisoformat("2021-02-01 13:45:01")
        test_date4 = datetime.fromisoformat("2021-03-01 14:50:12")
        test_tags = [
            "shortTag",
            '"tag - with quotes"',
            '"\\nt3$T "edg€ case! "',
            '\\""',
        ]
        test_annotation = "this interval is for testing purposes only"

        test_interval1 = Interval(
            start=test_date1, end=test_date2, tags=test_tags, annotation=test_annotation
        )
        test_interval2 = Interval(start=test_date1, end=test_date2)
        test_interval3 = Interval(
            start=test_date3, end=test_date4, annotation="foo bar"
        )
        test_interval4 = Interval(start=test_date2, end=test_date3)

        expt_date1 = "20210123T134659Z"
        expt_date2 = "20210124T020043Z"
        expt_date3 = "20210201T134501Z"
        expt_date4 = "20210301T145012Z"
        expt_tags = 'shortTag "tag - with quotes" "\\nt3$T "edg€ case! " \\""'
        expt_annotation = "this interval is for testing purposes only"

        expt_interval_str1 = (
            "inc "
            + expt_date1
            + " - "
            + expt_date2
            + " # "
            + expt_tags
            + " # "
            + expt_annotation
        )
        expt_interval_str2 = "inc " + expt_date1 + " - " + expt_date2
        expt_interval_str3 = (
            "inc " + expt_date3 + " - " + expt_date4 + " # # " + "foo bar"
        )
        expt_interval_str4 = "inc " + expt_date2 + " - " + expt_date3
        expt_file_name1 = "2021-01.data"
        expt_file_name2 = "2021-02.data"

        # Test with similar intervals
        test_interval_dict = to_monthly_data([test_interval1, test_interval2])
        expt_interval_dict = {
            expt_file_name1: expt_interval_str1 + "\n" + expt_interval_str2
        }
        assert test_interval_dict == expt_interval_dict

        # Test with unsorted intervals
        test_interval_dict = to_monthly_data([test_interval4, test_interval2])
        expt_interval_dict = {
            expt_file_name1: expt_interval_str2 + "\n" + expt_interval_str4
        }
        assert test_interval_dict == expt_interval_dict

        # Test with multiple months
        test_interval_dict = to_monthly_data(
            [test_interval1, test_interval2, test_interval3]
        )
        expt_interval_dict = {
            expt_file_name1: expt_interval_str1 + "\n" + expt_interval_str2,
            expt_file_name2: expt_interval_str3,
        }
        assert test_interval_dict == expt_interval_dict


class TestGetFileName:
    def test_no_start_time(self):
        """Tests invalid intervals."""
        with pytest.raises(RuntimeError):
            get_file_name(Interval())

        with pytest.raises(RuntimeError):
            test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
            get_file_name(Interval(end=test_date2, tags=["foo", "bar"]))

    def test_short_entry(self):
        """Tests for correct name extraction from start time."""
        test_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
        test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        test_date3 = datetime.fromisoformat("2021-02-01 13:45:01")
        test_interval2 = Interval(start=test_date1, end=test_date2)
        test_interval4 = Interval(start=test_date2, end=test_date3)
        expt_file_name1 = "2021-01.data"

        assert get_file_name(test_interval2) == expt_file_name1
        assert get_file_name(test_interval4) == expt_file_name1


class TestExtractTags:
    def test_no_entry(self):
        assert extract_tags([]) == ""

    def test_no_tags(self):
        date1 = datetime(2020, 1, 1)
        date2 = datetime(2021, 5, 29)
        date3 = datetime(2022, 7, 15)
        date4 = datetime(2023, 10, 11)
        i1 = Interval(start=date1, end=date2)
        i2 = Interval(start=date2, end=date3)
        i3 = Interval(start=date3, end=date4)
        assert extract_tags([i1, i2, i3]) == ""

    def test_mixed_input(self):
        date1 = datetime(2020, 1, 1)
        date2 = datetime(2021, 5, 29)
        date3 = datetime(2022, 7, 15)
        date4 = datetime(2023, 10, 11)
        i1 = Interval(start=date1, end=date2)
        i2 = Interval(
            start=date2, end=date3, tags=["tag1", "tag2", "tag3", "tag4", "tag1"]
        )
        i3 = Interval(
            start=date3, end=date4, tags=["tag2"], annotation="I am the annotation."
        )
        i4 = Interval(
            start=date1,
            end=date3,
            tags=["tag3", "tag2"],
            annotation="I am another annotation.",
        )
        i5 = Interval(start=date3, end=date4, annotation="I am the third annotation.")
        assert (
            extract_tags([i1, i2, i3, i4, i5])
            == '{"tag1":{"count":2},"tag2":{"count":3},"tag3":{"count":2},"tag4":{"count":1}}'
        )
