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

import pytest

from timewsync.interval import Interval, _strip_double_quotes, _quote_tag_if_needed


class TestIntervalFromDict:
    def test_empty_dict(self):
        """Test with an empty dictionary."""
        test_interval_dict = {}
        expt_interval = Interval()
        assert Interval.from_dict(**test_interval_dict) == expt_interval

    def test_valid_dict(self):
        """Test with a valid dictionary."""
        test_interval_dict = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this is an annotation",
        }
        expt_interval = Interval(
            start=datetime.fromisoformat("2021-01-24 02:00:43"),
            end=datetime.fromisoformat("2021-01-24 08:01:30"),
            tags=["foo", "bar"],
            annotation="this is an annotation",
        )
        assert Interval.from_dict(**test_interval_dict) == expt_interval


class TestIntervalToString:
    def test_syntax_tree(self):
        """Test the interval syntax tree, which covers all possible combinations to assemble an interval string.

        Syntax (tokens separated by whitespace):
            'inc' [ <iso> [ '-' <iso> ]] [[ '#' <tag> [ <tag> ... ]] | [ '#' [ <tag> ... ] '#' <annotation> ]]
        Covers all 18 paths of the syntax tree, sorted by number of arguments.
        """
        test_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
        test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        test_tags = [
            "shortTag",
            "tag - with quotes",
            '\\nt3$T \\"edg€ case! ',
            '\\""',
        ]
        test_annotation = "this interval is for testing purposes only"

        expt_date1 = "20210123T134659Z"
        expt_date2 = "20210124T020043Z"
        expt_tags = 'shortTag "tag - with quotes" "\\nt3$T \\"edg€ case! " "\\"""'
        expt_annotation = "this interval is for testing purposes only"

        partial_interval = Interval()
        assert str(partial_interval) == "inc"

        partial_interval = Interval(start=test_date1)
        assert str(partial_interval) == "inc " + expt_date1

        partial_interval = Interval(tags=["foo"])
        assert str(partial_interval) == "inc # foo"

        partial_interval = Interval(tags=test_tags)
        assert str(partial_interval) == "inc # " + expt_tags

        partial_interval = Interval(annotation=test_annotation)
        assert str(partial_interval) == f'inc # # "{expt_annotation}"'

        partial_interval = Interval(start=test_date1, end=test_date2)
        assert str(partial_interval) == "inc " + expt_date1 + " - " + expt_date2

        partial_interval = Interval(start=test_date1, tags=["foo"])
        assert str(partial_interval) == "inc " + expt_date1 + " # " + "foo"

        partial_interval = Interval(start=test_date1, tags=test_tags)
        assert str(partial_interval) == "inc " + expt_date1 + " # " + expt_tags

        partial_interval = Interval(start=test_date1, annotation=test_annotation)
        assert str(partial_interval) == f'inc {expt_date1} # # "{expt_annotation}"'

        partial_interval = Interval(tags=["foo"], annotation=test_annotation)
        assert str(partial_interval) == f'inc # foo # "{expt_annotation}"'

        partial_interval = Interval(tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == f'inc # {expt_tags} # "{expt_annotation}"'

        partial_interval = Interval(start=test_date1, end=test_date2, tags=["foo"])
        assert str(partial_interval) == "inc " + expt_date1 + " - " + expt_date2 + " # " + "foo"

        partial_interval = Interval(start=test_date1, end=test_date2, tags=test_tags)
        assert str(partial_interval) == "inc " + expt_date1 + " - " + expt_date2 + " # " + expt_tags

        partial_interval = Interval(start=test_date1, end=test_date2, annotation=test_annotation)
        assert str(partial_interval) == f'inc {expt_date1} - {expt_date2} # # "{expt_annotation}"'

        partial_interval = Interval(start=test_date1, tags=["foo"], annotation=test_annotation)
        assert str(partial_interval) == f'inc {expt_date1} # foo # "{expt_annotation}"'

        partial_interval = Interval(start=test_date1, tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == f'inc {expt_date1} # {expt_tags} # "{expt_annotation}"'

        partial_interval = Interval(start=test_date1, end=test_date2, tags=["foo"], annotation=test_annotation)
        assert str(partial_interval) == f'inc {expt_date1} - {expt_date2} # foo # "{expt_annotation}"'

        partial_interval = Interval(start=test_date1, end=test_date2, tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == f'inc {expt_date1} - {expt_date2} # {expt_tags} # "{expt_annotation}"'

    def test_ambiguous_interval(self):
        """Test an interval without start but with end time, which is ignored at the conversion."""
        test_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        wrong_interval = Interval(end=test_date2)
        assert str(wrong_interval) == "inc"


class TestIntervalToDict:
    def test_empty_interval(self):
        """Test with an empty Interval object."""
        test_interval = Interval()
        expt_interval_dict = {"start": "", "end": "", "tags": [], "annotation": ""}
        assert Interval.asdict(test_interval) == expt_interval_dict

    def test_valid_interval(self):
        """Test with a valid Interval object."""
        test_interval = Interval(
            start=datetime.fromisoformat("2021-01-24 02:00:43"),
            end=datetime.fromisoformat("2021-01-24 08:01:30"),
            tags=["foo", "bar"],
            annotation="this is an annotation",
        )
        expt_interval_dict = {
            "start": "20210124T020043Z",
            "end": "20210124T080130Z",
            "tags": ["foo", "bar"],
            "annotation": "this is an annotation",
        }
        assert Interval.asdict(test_interval) == expt_interval_dict


class TestAsInterval:
    def test_syntax_tree(self):
        """Test the interval syntax tree, which covers all possible combinations to assemble an Interval.

        Syntax (tokens separated by whitespace):
            'inc' [ <iso> [ '-' <iso> ]] [[ '#' <tag> [ <tag> ... ]] | [ '#' [ <tag> ... ] '#' <annotation> ]]
        Covers all 18 paths of the syntax tree, sorted by number of arguments.
        """
        test_date1 = "20210123T134659Z"
        test_date2 = "20210124T020043Z"
        test_tags = 'shortTag "tag - with quotes" "\\nt3$T \\"edg€ case! " \\""'
        test_annotation = "this interval is for testing purposes only"

        expt_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
        expt_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        expt_tags = [
            "shortTag",
            "tag - with quotes",
            '\\nt3$T \\"edg€ case! ',
            '\\""',
        ]
        expt_annotation = "this interval is for testing purposes only"

        interval_str = "inc"
        assert Interval.from_interval_str(interval_str) == Interval()

        interval_str = "inc " + test_date1
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1)

        interval_str = "inc # foo"
        assert Interval.from_interval_str(interval_str) == Interval(tags=["foo"])

        interval_str = "inc # " + test_tags
        assert Interval.from_interval_str(interval_str) == Interval(tags=expt_tags)

        interval_str = f'inc # # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(annotation=expt_annotation)

        interval_str = "inc " + test_date1 + " - " + test_date2
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1, end=expt_date2)

        interval_str = "inc " + test_date1 + " # " + "foo"
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1, tags=["foo"])

        interval_str = "inc " + test_date1 + " # " + test_tags
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1, tags=expt_tags)

        interval_str = f'inc {test_date1} # # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1, annotation=expt_annotation)

        interval_str = f'inc # foo # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(tags=["foo"], annotation=expt_annotation)

        interval_str = f'inc # {test_tags} # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(tags=expt_tags, annotation=expt_annotation)

        interval_str = "inc " + test_date1 + " - " + test_date2 + " # " + "foo"
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1, end=expt_date2, tags=["foo"])

        interval_str = "inc " + test_date1 + " - " + test_date2 + " # " + test_tags
        assert Interval.from_interval_str(interval_str) == Interval(start=expt_date1, end=expt_date2, tags=expt_tags)

        interval_str = f'inc {test_date1} - {test_date2} # # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(
            start=expt_date1, end=expt_date2, annotation=expt_annotation
        )

        interval_str = f'inc {test_date1} # foo # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(
            start=expt_date1, tags=["foo"], annotation=expt_annotation
        )

        interval_str = f'inc {test_date1} # {test_tags} # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(
            start=expt_date1, tags=expt_tags, annotation=expt_annotation
        )

        interval_str = f'inc {test_date1} - {test_date2} # foo # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(
            start=expt_date1, end=expt_date2, tags=["foo"], annotation=expt_annotation
        )

        interval_str = f'inc {test_date1} - {test_date2} # {test_tags} # "{test_annotation}"'
        assert Interval.from_interval_str(interval_str) == Interval(
            start=expt_date1, end=expt_date2, tags=expt_tags, annotation=expt_annotation
        )

    def test_invalid_strings(self):
        """Test invalid interval strings."""
        with pytest.raises(ValueError):
            Interval.from_interval_str("")

        with pytest.raises(ValueError):
            Interval.from_interval_str("20210123T134659Z - 20210124T020043Z")

        with pytest.raises(ValueError):
            Interval.from_interval_str("dec # thisIsNoValidInterval")

        with pytest.raises(ValueError):
            Interval.from_interval_str("inc#thisIsNoValidInterval")

        with pytest.raises(ValueError):
            Interval.from_interval_str("inc\\n#\\nthisIsNoValidInterval")

        with pytest.raises(ValueError):
            Interval.from_interval_str("inc 1")


class TestStripDoubleQuotes:
    def test_empty_string(self):
        assert _strip_double_quotes("") == ""
        assert _strip_double_quotes('""') == ""

    def test_one_double_quote(self):
        assert _strip_double_quotes('"') == '"'

    def test_standard_case(self):
        assert _strip_double_quotes('"foo"') == "foo"
        assert _strip_double_quotes('"two or more words"') == "two or more words"

    def test_length_2(self):
        assert _strip_double_quotes('"ab"') == "ab"
        assert _strip_double_quotes('"12"') == "12"
        assert _strip_double_quotes('"x-"') == "x-"
        assert _strip_double_quotes('"x""') == 'x"'
        assert _strip_double_quotes('""x"') == '"x'

    def test_quotes_at_start_or_end(self):
        assert _strip_double_quotes('abc""') == 'abc""'
        assert _strip_double_quotes('abc"') == 'abc"'
        assert _strip_double_quotes('""ab') == '""ab'
        assert _strip_double_quotes('"ab') == '"ab'

    def test_quotes_in_middle(self):
        assert _strip_double_quotes('ab"c') == 'ab"c'

    def test_no_quotes(self):
        assert _strip_double_quotes("abc") == "abc"
        assert _strip_double_quotes("012") == "012"
        assert _strip_double_quotes("a3b") == "a3b"


class TestQuoteTagIfNeeded:
    def test_single_word(self):
        data = "Bananas"
        assert _quote_tag_if_needed(data) == data

    def test_spaces(self):
        data = "Tag with spaces"
        expected = '"Tag with spaces"'
        assert _quote_tag_if_needed(data) == expected

    def test_special_chars(self):
        data = "tag_with_special_chars"
        expected = '"tag_with_special_chars"'
        assert _quote_tag_if_needed(data) == expected

    def test_already_quoted(self):
        data = '"Bananas"'
        assert _quote_tag_if_needed(data) == data
