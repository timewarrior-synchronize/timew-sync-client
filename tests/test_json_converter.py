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


import json

from timewsync.interval import Interval
from timewsync.json_converter import to_json_request, from_json_response, to_json_tags, from_json_error_response


class TestToJSONRequest:
    def test_empty_diff(self):
        expt_json = '{"userID": 1, "added": [], "removed": []}'
        assert to_json_request(1, ([], [])) == expt_json

    def test_added_empty(self):
        test_interval = {"start": "", "end": "", "tags": [], "annotation": ""}
        expt_json = '{"userID": 1, "added": [' + json.dumps(test_interval) + '], "removed": []}'
        result = to_json_request(1, ([Interval()], []))
        assert result == expt_json

    def test_added_filled(self):
        test_interval = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this has been added",
        }
        expt_json = '{"userID": 42, "added": [' + json.dumps(test_interval) + '], "removed": []}'
        result = to_json_request(42, ([Interval.from_dict(**test_interval)], []))
        assert result == expt_json

    def test_added_multiple(self):
        test_intervals = [
            {
                "start": "20210124T020043Z",
                "end": "20210124T080130Z",
                "tags": ["foo", "bar"],
                "annotation": "this has been added",
            },
            {"start": "20210321T170613Z", "end": "20210321T203246Z", "tags": [], "annotation": ""},
        ]
        expt_json = '{"userID": 128, "added": ' + json.dumps(test_intervals) + ', "removed": []}'
        result = to_json_request(128, ([Interval.from_dict(**i) for i in test_intervals], []))
        assert result == expt_json

    def test_removed_empty(self):
        test_interval = {"start": "", "end": "", "tags": [], "annotation": ""}
        expt_json = '{"userID": 1, "added": [], "removed": [' + json.dumps(test_interval) + "]}"
        result = to_json_request(1, ([], [Interval()]))
        assert result == expt_json

    def test_removed_filled(self):
        test_interval = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this has been removed",
        }
        expt_json = '{"userID": 42, "added": [], "removed": [' + json.dumps(test_interval) + "]}"
        result = to_json_request(42, ([], [Interval.from_dict(**test_interval)]))
        assert result == expt_json

    def test_removed_multiple(self):
        test_intervals = [
            {
                "start": "20210124T020043Z",
                "end": "20210124T080130Z",
                "tags": ["foo", "bar"],
                "annotation": "this has been removed",
            },
            {"start": "20210321T170613Z", "end": "20210321T203246Z", "tags": [], "annotation": ""},
        ]
        expt_json = '{"userID": 128, "added": [], "removed": ' + json.dumps(test_intervals) + "}"
        result = to_json_request(128, ([], [Interval.from_dict(**i) for i in test_intervals]))
        assert result == expt_json

    def test_both_empty(self):
        test_interval = {"start": "", "end": "", "tags": [], "annotation": ""}
        expt_json = (
            '{"userID": 1, "added": ['
            + json.dumps(test_interval)
            + '], "removed": ['
            + json.dumps(test_interval)
            + "]}"
        )
        result = to_json_request(1, ([Interval()], [Interval()]))
        assert result == expt_json

    def test_both_filled(self):
        test_interval = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this has been added/removed",
        }
        expt_json = (
            '{"userID": 42, "added": ['
            + json.dumps(test_interval)
            + '], "removed": ['
            + json.dumps(test_interval)
            + "]}"
        )
        result = to_json_request(42, ([Interval.from_dict(**test_interval)], [Interval.from_dict(**test_interval)]))
        assert result == expt_json

    def test_both_multiple(self):
        test_intervals = [
            {
                "start": "20210124T020043Z",
                "end": "20210124T080130Z",
                "tags": ["foo", "bar"],
                "annotation": "this has been added/removed",
            },
            {"start": "20210321T170613Z", "end": "20210321T203246Z", "tags": [], "annotation": ""},
        ]
        expt_json = (
            '{"userID": 128, "added": '
            + json.dumps(test_intervals)
            + ', "removed": '
            + json.dumps(test_intervals)
            + "}"
        )
        result = to_json_request(
            128, ([Interval.from_dict(**i) for i in test_intervals], [Interval.from_dict(**i) for i in test_intervals])
        )
        assert result == expt_json


class TestFromJSONResponse:
    def test_conflict_flag_false(self):
        test_json = '{"conflictsOccurred": false, "intervals": []}'
        _, c_flag = from_json_response(test_json)
        assert c_flag is False

    def test_conflict_flag_true(self):
        test_json = '{"conflictsOccurred": true, "intervals": []}'
        _, c_flag = from_json_response(test_json)
        assert c_flag is True

    def test_empty_interval(self):
        test_json = '{"conflictsOccurred": false, "intervals": [{}]}'
        expt_interval = Interval()
        result, _ = from_json_response(test_json)
        assert len(result) == 1
        assert result[0] == expt_interval

    def test_filled_interval(self):
        test_interval = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this is an annotation",
        }
        test_json = '{"conflictsOccurred": false, "intervals": [' + json.dumps(test_interval) + "]}"
        expt_interval = Interval.from_dict(**test_interval)
        result, _ = from_json_response(test_json)
        assert len(result) == 1
        assert result[0] == expt_interval

    def test_multiple_intervals(self):
        test_intervals = [
            {
                "start": "20210124T020043Z",
                "end": "20210124T080130Z",
                "tags": ["foo", "bar"],
                "annotation": "this is an annotation",
            },
            {"start": "20210321T170613Z", "end": "20210321T203246Z", "tags": [], "annotation": ""},
        ]
        test_json = '{"conflictsOccurred": false, "intervals": ' + json.dumps(test_intervals) + "}"
        expt_intervals = [Interval.from_dict(**test_intervals[0]), Interval.from_dict(**test_intervals[1])]
        result, _ = from_json_response(test_json)
        assert len(result) == 2
        assert result[0] == expt_intervals[0] and result[1] == expt_intervals[1]


class TestToJSONTags:
    def test_empty_tags(self):
        test_json = to_json_tags({})
        test_dict = json.loads(test_json)
        assert test_dict == {}

    def test_single_tag(self):
        test_tags = {"foo": 1}
        test_json = to_json_tags(test_tags)
        test_dict = json.loads(test_json)
        expt_dict = {"foo": {"count": 1}}
        assert test_dict == expt_dict

    def test_multiple_tags(self):
        test_tags = {"foo": 2, "bar": 5}
        test_json = to_json_tags(test_tags)
        test_dict = json.loads(test_json)
        expt_dict = {"foo": {"count": 2}, "bar": {"count": 5}}
        assert test_dict == expt_dict

    def test_quote_tags(self):
        test_tags = {'"': 0, '""': 10}
        test_json = to_json_tags(test_tags)
        test_dict = json.loads(test_json)
        expt_dict = {'"': {"count": 0}, '""': {"count": 10}}
        assert test_dict == expt_dict

    def test_escaped_tags(self):
        test_tags = {'\\"foo\\"': 1}
        test_json = to_json_tags(test_tags)
        test_dict = json.loads(test_json)
        expt_dict = {'"foo"': {"count": 1}}
        assert test_dict == expt_dict


class TestFromJSONErrorResponse:
    def test_simple_message_and_details(self):
        test_json = '{"message": "Houston, we have a problem", "details": "We\'ve had a Main B Bus Undervolt."}'
        message, details = from_json_error_response(test_json)
        assert message == "Houston, we have a problem"
        assert details == "We've had a Main B Bus Undervolt."
