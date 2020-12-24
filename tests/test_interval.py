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
    def test_syntax_tree(self):
        """Tests the interval syntax tree, which covers all possible combinations to assemble an interval string.

        Syntax (tokens separated by whitespace):
            'inc' [ <iso> [ '-' <iso> ]] [ '#' [ <tag> [ <tag> ... ]] [ '#' <annotation> ]]
        Covers all 18 paths of the syntax tree, sorted by number of arguments.
        """
        test_date1 = datetime.fromisoformat('2021-01-23 13:46:59')
        test_date2 = datetime.fromisoformat('2021-01-24 02:00:43')
        test_tags = ['shortTag', '"tag - with quotes"', '"\\nt3$T \"edg€ case! \"', '\\\""']
        test_annotation = 'this interval is for testing purposes only'

        expt_date1 = '20210123T134659Z'
        expt_date2 = '20210124T020043Z'
        expt_tags = 'shortTag "tag - with quotes" "\\nt3$T \"edg€ case! \" \\\""'
        expt_annotation = 'this interval is for testing purposes only'

        partial_interval = Interval()
        assert str(partial_interval) == 'inc'

        partial_interval = Interval(start=test_date1)
        assert str(partial_interval) == 'inc ' + expt_date1

        partial_interval = Interval(tags=['foo'])
        assert str(partial_interval) == 'inc # foo'

        partial_interval = Interval(tags=test_tags)
        assert str(partial_interval) == 'inc # ' + expt_tags

        partial_interval = Interval(annotation=test_annotation)
        assert str(partial_interval) == 'inc # # ' + expt_annotation

        partial_interval = Interval(start=test_date1, end=test_date2)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' - ' + expt_date2

        partial_interval = Interval(start=test_date1, tags=['foo'])
        assert str(partial_interval) == 'inc ' + expt_date1 + ' # ' + 'foo'

        partial_interval = Interval(start=test_date1, tags=test_tags)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' # ' + expt_tags

        partial_interval = Interval(start=test_date1, annotation=test_annotation)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' # # ' + expt_annotation

        partial_interval = Interval(tags=['foo'], annotation=test_annotation)
        assert str(partial_interval) == 'inc # ' + 'foo' + ' # ' + expt_annotation

        partial_interval = Interval(tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == 'inc # ' + expt_tags + ' # ' + expt_annotation

        partial_interval = Interval(start=test_date1, end=test_date2, tags=['foo'])
        assert str(partial_interval) == 'inc ' + expt_date1 + ' - ' + expt_date2 + ' # ' + 'foo'

        partial_interval = Interval(start=test_date1, end=test_date2, tags=test_tags)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' - ' + expt_date2 + ' # ' + expt_tags

        partial_interval = Interval(start=test_date1, end=test_date2, annotation=test_annotation)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' - ' + expt_date2 + ' # # ' + expt_annotation

        partial_interval = Interval(start=test_date1, tags=['foo'], annotation=test_annotation)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' # ' + 'foo' + ' # ' + expt_annotation

        partial_interval = Interval(start=test_date1, tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' # ' + expt_tags + ' # ' + expt_annotation

        partial_interval = Interval(start=test_date1, end=test_date2, tags=['foo'], annotation=test_annotation)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' - ' + expt_date2 + ' # ' + 'foo' + ' # ' + expt_annotation

        partial_interval = Interval(start=test_date1, end=test_date2, tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == 'inc ' + expt_date1 + ' - ' + expt_date2 + ' # ' + expt_tags + ' # ' + expt_annotation

    def test_wrong_interval(self):
        """Tests an interval without start but with end time, which is ignored at the conversion."""
        test_date2 = datetime.fromisoformat('2021-01-24 02:00:43')
        wrong_interval = Interval(end=test_date2)
        assert str(wrong_interval) == 'inc'


class TestAsInterval:
    def test_syntax_tree(self):
        """Tests the interval syntax tree, which covers all possible combinations to assemble an Interval.

        Syntax (tokens separated by whitespace):
            'inc' [ <iso> [ '-' <iso> ]] [ '#' [ <tag> [ <tag> ... ]] [ '#' <annotation> ]]
        Covers all 18 paths of the syntax tree, sorted by number of arguments.
        """
        test_date1 = '20210123T134659Z'
        test_date2 = '20210124T020043Z'
        test_tags = 'shortTag "tag - with quotes" "\\nt3$T \"edg€ case! \" \\\""'
        test_annotation = 'this interval is for testing purposes only'

        expt_date1 = datetime.fromisoformat('2021-01-23 13:46:59')
        expt_date2 = datetime.fromisoformat('2021-01-24 02:00:43')
        expt_tags = ['shortTag', '"tag - with quotes"', '"\\nt3$T \"edg€ case! \"', '\\\""']
        expt_annotation = 'this interval is for testing purposes only'

        interval_str = 'inc'
        assert as_interval(interval_str) == Interval()

        interval_str = 'inc ' + test_date1
        assert as_interval(interval_str) == Interval(start=expt_date1)

        interval_str = 'inc # foo'
        assert as_interval(interval_str) == Interval(tags=['foo'])

        interval_str = 'inc # ' + test_tags
        assert as_interval(interval_str) == Interval(tags=expt_tags)

        interval_str = 'inc # # ' + test_annotation
        assert as_interval(interval_str) == Interval(annotation=expt_annotation)

        interval_str = 'inc ' + test_date1 + ' - ' + test_date2
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2)

        interval_str = 'inc ' + test_date1 + ' # ' + 'foo'
        assert as_interval(interval_str) == Interval(start=expt_date1, tags=['foo'])

        interval_str = 'inc ' + test_date1 + ' # ' + test_tags
        assert as_interval(interval_str) == Interval(start=expt_date1, tags=expt_tags)

        interval_str = 'inc ' + test_date1 + ' # # ' + test_annotation
        assert as_interval(interval_str) == Interval(start=expt_date1, annotation=expt_annotation)

        interval_str = 'inc # ' + 'foo' + ' # ' + test_annotation
        assert as_interval(interval_str) == Interval(tags=['foo'], annotation=expt_annotation)

        interval_str = 'inc # ' + test_tags + ' # ' + test_annotation
        assert as_interval(interval_str) == Interval(tags=expt_tags, annotation=expt_annotation)

        interval_str = 'inc ' + test_date1 + ' - ' + test_date2 + ' # ' + 'foo'
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2, tags=['foo'])

        interval_str = 'inc ' + test_date1 + ' - ' + test_date2 + ' # ' + test_tags
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2, tags=expt_tags)

        interval_str = 'inc ' + test_date1 + ' - ' + test_date2 + ' # # ' + test_annotation
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2, annotation=expt_annotation)

        interval_str = 'inc ' + test_date1 + ' # ' + 'foo' + ' # ' + test_annotation
        assert as_interval(interval_str) == Interval(start=expt_date1, tags=['foo'], annotation=expt_annotation)

        interval_str = 'inc ' + test_date1 + ' # ' + test_tags + ' # ' + test_annotation
        assert as_interval(interval_str) == Interval(start=expt_date1, tags=expt_tags, annotation=expt_annotation)

        interval_str = 'inc ' + test_date1 + ' - ' + test_date2 + ' # ' + 'foo' + ' # ' + test_annotation
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2, tags=['foo'], annotation=expt_annotation)

        interval_str = 'inc ' + test_date1 + ' - ' + test_date2 + ' # ' + test_tags + ' # ' + test_annotation
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2, tags=expt_tags, annotation=expt_annotation)

    def test_wrong_string(self):
        """Tests interval strings without the required 'inc' keyword."""
        with pytest.raises(RuntimeError):
            assert as_interval('') == Interval()

        with pytest.raises(RuntimeError):
            as_interval('dec # thisIsNoValidInterval')

        with pytest.raises(RuntimeError):
            as_interval('inc#thisIsNoValidInterval')

        with pytest.raises(RuntimeError):
            as_interval('inc\\n#\\nthisIsNoValidInterval')

        # TODO line 'inc 2' should not work, maybe? resolve before merging (assignee: Arne)


class TestTokenize:
    def test_nothing(self):
        # tokenize('inc 20201214T134735Z # \"16-update json-format\" "thisIsATest"')
        pass
