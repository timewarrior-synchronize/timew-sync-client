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

from timewsync.interval import Interval
from timewsync.json_converter import to_json_request, to_interval_list


def test_to_json_request():
    test_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
    test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
    test_tags = ["shortTag", '"tag - with quotes"', '"\\nt3$T "edg€ case! "', '\\""']
    test_annotation = "this interval is for testing purposes only"

    test_interval1 = Interval(start=test_date1, end=test_date2)
    test_interval2 = Interval(
        start=test_date1, end=test_date2, tags=test_tags, annotation=test_annotation
    )
    test_interval_list = [test_interval1, test_interval2]

    expt_interval1_str = "inc 20210123T134659Z - 20210124T020043Z"
    expt_interval2_str = 'inc 20210123T134659Z - 20210124T020043Z # shortTag \\"tag - with quotes\\" \\"\\\\nt3$T \\"edg\\u20ac case! \\" \\\\\\"\\" # this interval is for testing purposes only'

    expt_json_request = (
        """{
  "userId": 1,
  "clientId": 1,
  "intervalData": [
    \""""
        + expt_interval1_str
        + """\",
    \""""
        + expt_interval2_str
        + """\"
  ]\n}"""
    )

    test_json_request = to_json_request(test_interval_list)
    assert test_json_request == expt_json_request


def test_to_interval_list():
    test_interval1_str = "inc 20210123T134659Z - 20210124T020043Z"
    test_interval2_str = 'inc 20210123T134659Z - 20210124T020043Z # shortTag \\"tag - with quotes\\" \\"\\\\nt3$T \\"edg\\u20ac case! \\" \\\\\\"\\" # this interval is for testing purposes only'

    expt_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
    expt_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
    expt_tags = ["shortTag", '"tag - with quotes"', '"\\nt3$T "edg€ case! "', '\\""']
    expt_annotation = "this interval is for testing purposes only"

    expt_interval1 = Interval(start=expt_date1, end=expt_date2)
    expt_interval2 = Interval(
        start=expt_date1, end=expt_date2, tags=expt_tags, annotation=expt_annotation
    )
    expt_interval_list = [expt_interval1, expt_interval2]

    test_json_response = (
        """{
    "intervalData": [
        \""""
        + test_interval1_str
        + """\",
        \""""
        + test_interval2_str
        + """\"
    ]\n}"""
    )

    test_interval_list = to_interval_list(test_json_response)
    assert len(test_interval_list) == 2
    assert test_interval_list[0] == expt_interval_list[0]
    assert test_interval_list[1] == expt_interval_list[1]
