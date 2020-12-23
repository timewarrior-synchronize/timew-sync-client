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

from timewsync.interval import Interval, as_interval


class TestIntervalToString:
    def test_empty(self):
        empty_interval = Interval()
        assert str(empty_interval) == 'inc'

    def test_partial(self):
        test_date1 = datetime.fromisoformat('2021-01-23 13:46:59')
        test_date2 = datetime.fromisoformat('2021-01-24 02:00:43')
        test_tags = ['shortTag', '"tag - with quotes"', '"\\\nt3$T \"edg€ case! \" \\\""']
        test_annotation = 'this interval is for testing purposes only'

        partial_interval = Interval(start=test_date1)
        assert str(partial_interval) == 'inc 20210123T134659Z'

        partial_interval = Interval(tags=['foo'])
        assert str(partial_interval) == 'inc # foo'

        partial_interval = Interval(tags=test_tags)
        assert str(partial_interval) == 'inc # shortTag "tag - with quotes" "\\\nt3$T \"edg€ case! \" \\\""'

        partial_interval = Interval(annotation=test_annotation)
        assert str(partial_interval) == 'inc # # this interval is for testing purposes only'

        partial_interval = Interval(start=test_date1, end=test_date2)
        assert str(partial_interval) == 'inc 20210123T134659Z - 20210124T020043Z'

        partial_interval = Interval(start=test_date1, tags=test_tags)
        assert str(partial_interval) == 'inc 20210123T134659Z # shortTag "tag - with quotes" "\\\nt3$T \"edg€ case! \" \\\""'

        partial_interval = Interval(start=test_date1, annotation=test_annotation)
        assert str(partial_interval) == 'inc 20210123T134659Z # # this interval is for testing purposes only'

        partial_interval = Interval(tags=['foo', 'bar'], annotation=test_annotation)
        assert str(partial_interval) == 'inc # foo bar # this interval is for testing purposes only'

        partial_interval = Interval(start=test_date1, end=test_date2, tags=['foo', 'bar'])
        assert str(partial_interval) == 'inc 20210123T134659Z - 20210124T020043Z # foo bar'

        partial_interval = Interval(start=test_date1, end=test_date2, annotation=test_annotation)
        assert str(partial_interval) == 'inc 20210123T134659Z - 20210124T020043Z # # this interval is for testing purposes only'

        partial_interval = Interval(start=test_date1, tags=['foo', 'bar'], annotation=test_annotation)
        assert str(partial_interval) == 'inc 20210123T134659Z # foo bar # this interval is for testing purposes only'

    def test_full(self):
        test_date1 = datetime.fromisoformat('2021-01-23 13:46:59')
        expt_date1 = '20210123T134659Z'
        test_date2 = datetime.fromisoformat('2021-01-24 02:00:43')
        expt_date2 = '20210124T020043Z'
        test_tags = ['shortTag', '"tag - with quotes"', '"\\\nt3$T \"edg€ case! \" \\\""']
        expt_tags = 'shortTag "tag - with quotes" "\\\nt3$T \"edg€ case! \" \\\""'
        test_annotation = 'this interval is for testing purposes only'
        expt_annotation = 'this interval is for testing purposes only'

        expected = 'inc'
        expected += ' ' + expt_date1
        expected += ' - ' + expt_date2
        expected += ' # ' + expt_tags
        expected += ' # ' + expt_annotation

        full_interval = Interval(test_date1, test_date2, test_tags, test_annotation)
        assert str(full_interval) == expected


class TestAsInterval:
    def test_nothing(self):
        # as_interval('inc 20201214T134735Z # \"16-update json-format\" "thisIsATest"')
        pass

    def test_raise(self):
        with pytest.raises(AssertionError):
            as_interval('')


class TestTokenize:
    def test_nothing(self):
        # tokenize('inc 20201214T134735Z # \"16-update json-format\" "thisIsATest"')
        pass
