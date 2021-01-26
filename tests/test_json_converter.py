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


import json
from datetime import datetime

from timewsync.interval import Interval
from timewsync.json_converter import to_json_request, from_json_response


class TestToJSONRequest:
    def test_empty_diff(self):
        """Test with empty diff."""
        expt_json = '{"userID": 1, "added": [], "removed": []}'
        assert to_json_request(1, ([], [])) == expt_json

    def test_added_only_diff(self):
        """Test with only the 'added' list having data."""

        # Test with empty Interval object
        test_interval = Interval()
        expt_interval_json = json.dumps(Interval.asdict(test_interval))
        expt_json = (
            '{"userID": 1, "added": [' + expt_interval_json + '], "removed": []}'
        )
        assert to_json_request(1, ([test_interval], [])) == expt_json

        # Test with filled Interval object
        test_interval = Interval(
            start=datetime.fromisoformat("2021-01-24 02:00:43"),
            end=datetime.fromisoformat("2021-01-24 08:01:30"),
            tags=["foo", "bar"],
            annotation="this has been added",
        )
        expt_interval_json = json.dumps(Interval.asdict(test_interval))
        expt_json = (
            '{"userID": 42, "added": [' + expt_interval_json + '], "removed": []}'
        )
        assert to_json_request(42, ([test_interval], [])) == expt_json
        expt_json = (
            '{"userID": 128, "added": ['
            + expt_interval_json
            + ", "
            + expt_interval_json
            + '], "removed": []}'
        )
        assert to_json_request(128, ([test_interval, test_interval], [])) == expt_json

    def test_removed_only_diff(self):
        """Test with only the 'removed' list having data."""

        # Test with empty Interval object
        test_interval = Interval()
        expt_interval_json = json.dumps(Interval.asdict(test_interval))
        expt_json = (
            '{"userID": 1, "added": [], "removed": [' + expt_interval_json + "]}"
        )
        assert to_json_request(1, ([], [test_interval])) == expt_json

        # Test with filled Interval object
        test_interval = Interval(
            start=datetime.fromisoformat("2021-01-24 02:00:43"),
            end=datetime.fromisoformat("2021-01-24 08:01:30"),
            tags=["foo", "bar"],
            annotation="this has been removed",
        )
        expt_interval_json = json.dumps(Interval.asdict(test_interval))
        expt_json = (
            '{"userID": 42, "added": [], "removed": [' + expt_interval_json + "]}"
        )
        assert to_json_request(42, ([], [test_interval])) == expt_json

        # Test with multiple filled Interval objects
        expt_json = (
            '{"userID": 128, "added": [], "removed": ['
            + expt_interval_json
            + ", "
            + expt_interval_json
            + "]}"
        )
        assert to_json_request(128, ([], [test_interval, test_interval])) == expt_json

    def test_full_diff(self):
        """Test with both lists of diff having data."""

        # Test with empty Interval objects
        test_added_interval = Interval()
        test_removed_interval = Interval()
        expt_added_interval_json = json.dumps(Interval.asdict(test_added_interval))
        expt_removed_interval_json = json.dumps(Interval.asdict(test_removed_interval))
        expt_json = (
            '{"userID": 1, "added": ['
            + expt_added_interval_json
            + '], "removed": ['
            + expt_removed_interval_json
            + "]}"
        )
        assert (
            to_json_request(1, ([test_added_interval], [test_removed_interval]))
            == expt_json
        )

        # Test with filled Interval objects
        test_added_interval = Interval(
            start=datetime.fromisoformat("2021-01-24 02:00:43"),
            end=datetime.fromisoformat("2021-01-24 08:01:30"),
            tags=["foo", "bar"],
            annotation="this has been added",
        )
        test_removed_interval = Interval(
            start=datetime.fromisoformat("2021-01-24 02:00:43"),
            end=datetime.fromisoformat("2021-01-24 08:01:30"),
            tags=["foo", "bar"],
            annotation="this has been removed",
        )
        expt_added_interval_json = json.dumps(Interval.asdict(test_added_interval))
        expt_removed_interval_json = json.dumps(Interval.asdict(test_removed_interval))
        expt_json = (
            '{"userID": 42, "added": ['
            + expt_added_interval_json
            + '], "removed": ['
            + expt_removed_interval_json
            + "]}"
        )
        assert (
            to_json_request(42, ([test_added_interval], [test_removed_interval]))
            == expt_json
        )

        # Test with multiple filled Interval objects
        expt_json = (
            '{"userID": 128, "added": ['
            + expt_added_interval_json
            + ", "
            + expt_added_interval_json
            + '], "removed": ['
            + expt_removed_interval_json
            + ", "
            + expt_removed_interval_json
            + "]}"
        )
        assert (
            to_json_request(
                128,
                (
                    [test_added_interval, test_added_interval],
                    [test_removed_interval, test_removed_interval],
                ),
            )
            == expt_json
        )


class TestFromJSONResponse:
    def test_conflict_flag(self):
        """Test with empty list in json."""
        test_json = '{"conflictsOccurred": false, "intervals": []}'
        _, c_flag = from_json_response(test_json)
        assert c_flag is False
        test_json = '{"conflictsOccurred": true, "intervals": []}'
        _, c_flag = from_json_response(test_json)
        assert c_flag is True

    def test_interval_list(self):
        """Test with list in json having data."""

        # Test with empty interval
        test_interval_dict = {}
        test_interval_json = json.dumps(test_interval_dict)
        test_json = (
            '{"conflictsOccurred": false, "intervals": [' + test_interval_json + "]}"
        )
        expt_interval_list = [Interval()]
        result, _ = from_json_response(test_json)
        assert len(result) == 1
        assert result[0] == expt_interval_list[0]

        # Test with filled interval
        test_interval_dict = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this is an annotation",
        }
        test_interval_json = json.dumps(test_interval_dict)
        test_json = (
            '{"conflictsOccurred": false, "intervals": [' + test_interval_json + "]}"
        )
        expt_interval_list = [Interval.from_dict(test_interval_dict)]
        result, _ = from_json_response(test_json)
        assert len(result) == 1
        assert result[0] == expt_interval_list[0]

        # Test with multiple filled intervals
        test_json = (
            '{"conflictsOccurred": false, "intervals": ['
            + test_interval_json
            + ", "
            + test_interval_json
            + "]}"
        )
        expt_interval_list = [
            Interval.from_dict(test_interval_dict),
            Interval.from_dict(test_interval_dict),
        ]
        result, _ = from_json_response(test_json)
        assert len(result) == 2
        assert result[0] == expt_interval_list[0] and result[1] == expt_interval_list[1]
