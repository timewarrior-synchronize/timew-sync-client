###############################################################################
#
# Copyright 2020 - 2021, Jan Bormet, Anna-Felicitas Hausmann, Joachim Schmidt, Vincent Stollenwerk, Arne Turuc
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
from typing import List

import pytest

from timewsync.file_parser import (
    as_interval_list,
    as_file_strings,
    get_file_name,
    extract_tags,
)
from timewsync.interval import Interval


def _compare(intervals_1: List[Interval], intervals_2: List[Interval]):
    assert len(intervals_1) == len(intervals_2)
    intervals_1.sort(key=lambda i: i.start)
    intervals_2.sort(key=lambda i: i.start)
    for index in range(len(intervals_1)):
        assert intervals_1[index] == intervals_2[index]


class TestAsIntervalList:
    def test_active_tracking(self):
        test_interval = 'inc 20210124T020043Z # foo bar # "this is an annotation"'
        expt_time = datetime.fromisoformat("2021-01-24 02:00:43")
        expt_tags = ["foo", "bar"]
        expt_annotation = "this is an annotation"
        result_i, result_a = as_interval_list({"": test_interval})
        assert len(result_i) == 1 and result_a
        assert result_i[0].start == expt_time
        assert result_i[0].end
        assert result_i[0].tags == expt_tags
        assert result_i[0].annotation == expt_annotation
        assert result_a.start == result_i[0].end
        assert result_a.end is None
        assert result_a.tags == expt_tags
        assert result_a.annotation == expt_annotation

    def test_no_data(self):
        assert as_interval_list({}) == ([], None)
        assert as_interval_list({"2021-01.data": ""}) == ([], None)
        assert as_interval_list({"2021-01.data": "\n\n"}) == ([], None)

    def test_single_interval(self):
        test_intervals = {"2021-01.data": 'inc 20210124T020043Z - 20210124T080130Z # foo bar # "this is an annotation"'}
        expt_intervals = [
            Interval.from_dict(
                **{
                    "start": "20210124T020043Z",
                    "end": "20210124T080130Z",
                    "tags": ["foo", "bar"],
                    "annotation": "this is an annotation",
                }
            )
        ]
        result_i, result_a = as_interval_list(test_intervals)
        assert not result_a
        _compare(result_i, expt_intervals)

    def test_similar_intervals(self):
        test_intervals = {
            "2021-01.data": (
                'inc 20210124T020043Z - 20210124T080130Z # foo bar # "this is an annotation"'
                "\n"
                "inc 20210124T020043Z - 20210124T080130Z"
            )
        }
        expt_intervals = [
            Interval.from_dict(
                **{
                    "start": "20210124T020043Z",
                    "end": "20210124T080130Z",
                    "tags": ["foo", "bar"],
                    "annotation": "this is an annotation",
                }
            ),
            Interval.from_dict(**{"start": "20210124T020043Z", "end": "20210124T080130Z"}),
        ]
        result_i, result_a = as_interval_list(test_intervals)
        assert not result_a
        _compare(result_i, expt_intervals)

    def test_multiple_months(self):
        test_intervals = {
            "2021-01.data": 'inc 20210124T020043Z - 20210124T080130Z # foo bar # "this is an annotation"',
            "2021-02.data": 'inc 20210201T134501Z - 20210301T145012Z # "29 days"',
        }
        expt_intervals = [
            Interval.from_dict(
                **{
                    "start": "20210124T020043Z",
                    "end": "20210124T080130Z",
                    "tags": ["foo", "bar"],
                    "annotation": "this is an annotation",
                }
            ),
            Interval.from_dict(**{"start": "20210201T134501Z", "end": "20210301T145012Z", "tags": ["29 days"]}),
        ]
        result_i, result_a = as_interval_list(test_intervals)
        assert not result_a
        _compare(result_i, expt_intervals)


class TestAsFileStrings:
    def test_active_tracking_success(self):
        test_interval = Interval.from_dict(
            **{"start": "20210124T020043Z", "tags": ["foo", "bar"], "annotation": "this is an annotation"}
        )
        expt_intervals = {"2021-01.data": 'inc 20210124T020043Z # foo bar # "this is an annotation"'}
        file_strings, started_tracking = as_file_strings([], test_interval)
        assert file_strings == expt_intervals
        assert started_tracking is True

    def test_active_tracking_failure(self):
        test_interval = Interval.from_dict(
            **{"start": "20210124T020043Z", "tags": ["foo", "bar"], "annotation": "this is an annotation"}
        )
        conflicting_interval = Interval.from_dict(
            **{"start": "20210201T134501Z", "end": "20210301T145012Z", "tags": ["29 days"]}
        )
        expt_intervals = {"2021-02.data": 'inc 20210201T134501Z - 20210301T145012Z # "29 days"'}
        file_strings, started_tracking = as_file_strings([conflicting_interval], test_interval)
        assert file_strings == expt_intervals
        assert started_tracking is False

    def test_no_intervals(self):
        file_strings, started_tracking = as_file_strings([])
        assert file_strings == {}
        assert started_tracking is False

    def test_single_interval(self):
        test_intervals = [
            Interval.from_dict(
                **{
                    "start": "20210124T020043Z",
                    "end": "20210124T080130Z",
                    "tags": ["foo", "bar"],
                    "annotation": "this is an annotation",
                }
            )
        ]
        expt_intervals = {"2021-01.data": 'inc 20210124T020043Z - 20210124T080130Z # foo bar # "this is an annotation"'}
        file_strings, started_tracking = as_file_strings(test_intervals)
        assert file_strings == expt_intervals
        assert started_tracking is False

    def test_similar_intervals(self):
        test_intervals = [
            Interval.from_dict(
                **{
                    "start": "20210124T020043Z",
                    "end": "20210124T080130Z",
                    "tags": ["foo", "bar"],
                    "annotation": "this is an annotation",
                }
            ),
            Interval.from_dict(**{"start": "20210124T020043Z", "end": "20210124T080130Z"}),
        ]
        expt_intervals = {
            "2021-01.data": (
                'inc 20210124T020043Z - 20210124T080130Z # foo bar # "this is an annotation"'
                "\n"
                "inc 20210124T020043Z - 20210124T080130Z"
            )
        }
        file_strings, started_tracking = as_file_strings(test_intervals)
        assert file_strings == expt_intervals
        assert started_tracking is False

    def test_unsorted_intervals(self):
        test_intervals = [
            Interval.from_dict(
                **{"start": "20210124T020043Z", "end": "20210124T080130Z", "annotation": "this is the second interval"}
            ),
            Interval.from_dict(**{"start": "20210123T134659Z", "end": "20210124T020043Z"}),
        ]
        expt_intervals = {
            "2021-01.data": (
                "inc 20210123T134659Z - 20210124T020043Z"
                "\n"
                'inc 20210124T020043Z - 20210124T080130Z # # "this is the second interval"'
            )
        }
        file_strings, started_tracking = as_file_strings(test_intervals)
        assert file_strings == expt_intervals
        assert started_tracking is False

    def test_multiple_months(self):
        test_intervals = [
            Interval.from_dict(
                **{
                    "start": "20210124T020043Z",
                    "end": "20210124T080130Z",
                    "tags": ["foo", "bar"],
                    "annotation": "this is an annotation",
                }
            ),
            Interval.from_dict(**{"start": "20210201T134501Z", "end": "20210301T145012Z", "tags": ["29 days"]}),
        ]
        expt_intervals = {
            "2021-01.data": 'inc 20210124T020043Z - 20210124T080130Z # foo bar # "this is an annotation"',
            "2021-02.data": 'inc 20210201T134501Z - 20210301T145012Z # "29 days"',
        }
        file_strings, started_tracking = as_file_strings(test_intervals)
        assert file_strings == expt_intervals
        assert started_tracking is False


class TestGetFileName:
    def test_no_start_time(self):
        with pytest.raises(ValueError):
            get_file_name(Interval())

        with pytest.raises(ValueError):
            test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
            get_file_name(Interval(end=test_date2, tags=["foo", "bar"]))

    def test_short_entry(self):
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
        assert extract_tags([]) == "{}"

    def test_no_tags(self):
        date1 = datetime(2020, 1, 1)
        date2 = datetime(2021, 5, 29)
        date3 = datetime(2022, 7, 15)
        date4 = datetime(2023, 10, 11)
        i1 = Interval(start=date1, end=date2)
        i2 = Interval(start=date2, end=date3)
        i3 = Interval(start=date3, end=date4)
        assert extract_tags([i1, i2, i3]) == "{}"

    def test_mixed_input(self):
        date1 = datetime(2020, 1, 1)
        date2 = datetime(2021, 5, 29)
        date3 = datetime(2022, 7, 15)
        date4 = datetime(2023, 10, 11)
        i1 = Interval(start=date1, end=date2)
        i2 = Interval(
            start=date2,
            end=date3,
            tags=[
                "this is tag 1",
                'this is "not" tag 1',
                "tag2",
                "tag3",
                "tag4",
                "this is tag 1",
                "tag1",
            ],
        )
        i3 = Interval(start=date3, end=date4, tags=["tag2"], annotation="I am the annotation.")
        i4 = Interval(
            start=date1,
            end=date3,
            tags=["tag3", "tag2"],
            annotation="I am another annotation.",
        )
        i5 = Interval(start=date3, end=date4, annotation="I am the third annotation.")
        i6 = Interval(start=date1, end=date2, tags=['"', '"'])
        assert extract_tags([i1, i2, i3, i4, i5, i6]) == (
            "{"
            '\n  "this is tag 1": {'
            '\n    "count": 2'
            "\n  },"
            '\n  "this is \\"not\\" tag 1": {'
            '\n    "count": 1'
            "\n  },"
            '\n  "tag2": {'
            '\n    "count": 3'
            "\n  },"
            '\n  "tag3": {'
            '\n    "count": 2'
            "\n  },"
            '\n  "tag4": {'
            '\n    "count": 1'
            "\n  },"
            '\n  "tag1": {'
            '\n    "count": 1'
            "\n  },"
            '\n  "\\"": {'
            '\n    "count": 2'
            "\n  }"
            "\n}"
        )
