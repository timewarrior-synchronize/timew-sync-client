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

from timewsync.interval import Interval, as_interval, tokenize


class TestIntervalFromIntervalStr:
    def test_not_implemented(self):
        """Test for raised error."""
        with pytest.raises(NotImplementedError):
            Interval.from_interval_str()


class TestIntervalFromDict:
    def test_empty_dict(self):
        """Test with an empty dictionary."""
        test_interval_dict = {}
        expt_interval = Interval()
        assert Interval.from_dict(test_interval_dict) == expt_interval

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
        assert Interval.from_dict(test_interval_dict) == expt_interval


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
            '"tag - with quotes"',
            '"\\nt3$T "edg€ case! "',
            '\\""',
        ]
        test_annotation = "this interval is for testing purposes only"

        expt_date1 = "20210123T134659Z"
        expt_date2 = "20210124T020043Z"
        expt_tags = 'shortTag "tag - with quotes" "\\nt3$T "edg€ case! " \\""'
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
        assert str(partial_interval) == "inc # # " + expt_annotation

        partial_interval = Interval(start=test_date1, end=test_date2)
        assert str(partial_interval) == "inc " + expt_date1 + " - " + expt_date2

        partial_interval = Interval(start=test_date1, tags=["foo"])
        assert str(partial_interval) == "inc " + expt_date1 + " # " + "foo"

        partial_interval = Interval(start=test_date1, tags=test_tags)
        assert str(partial_interval) == "inc " + expt_date1 + " # " + expt_tags

        partial_interval = Interval(start=test_date1, annotation=test_annotation)
        assert str(partial_interval) == "inc " + expt_date1 + " # # " + expt_annotation

        partial_interval = Interval(tags=["foo"], annotation=test_annotation)
        assert str(partial_interval) == "inc # " + "foo" + " # " + expt_annotation

        partial_interval = Interval(tags=test_tags, annotation=test_annotation)
        assert str(partial_interval) == "inc # " + expt_tags + " # " + expt_annotation

        partial_interval = Interval(start=test_date1, end=test_date2, tags=["foo"])
        assert (
            str(partial_interval)
            == "inc " + expt_date1 + " - " + expt_date2 + " # " + "foo"
        )

        partial_interval = Interval(start=test_date1, end=test_date2, tags=test_tags)
        assert (
            str(partial_interval)
            == "inc " + expt_date1 + " - " + expt_date2 + " # " + expt_tags
        )

        partial_interval = Interval(
            start=test_date1, end=test_date2, annotation=test_annotation
        )
        assert (
            str(partial_interval)
            == "inc " + expt_date1 + " - " + expt_date2 + " # # " + expt_annotation
        )

        partial_interval = Interval(
            start=test_date1, tags=["foo"], annotation=test_annotation
        )
        assert (
            str(partial_interval)
            == "inc " + expt_date1 + " # " + "foo" + " # " + expt_annotation
        )

        partial_interval = Interval(
            start=test_date1, tags=test_tags, annotation=test_annotation
        )
        assert (
            str(partial_interval)
            == "inc " + expt_date1 + " # " + expt_tags + " # " + expt_annotation
        )

        partial_interval = Interval(
            start=test_date1, end=test_date2, tags=["foo"], annotation=test_annotation
        )
        assert (
            str(partial_interval)
            == "inc "
            + expt_date1
            + " - "
            + expt_date2
            + " # "
            + "foo"
            + " # "
            + expt_annotation
        )

        partial_interval = Interval(
            start=test_date1, end=test_date2, tags=test_tags, annotation=test_annotation
        )
        assert (
            str(partial_interval)
            == "inc "
            + expt_date1
            + " - "
            + expt_date2
            + " # "
            + expt_tags
            + " # "
            + expt_annotation
        )

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
        test_tags = 'shortTag "tag - with quotes" "\\nt3$T "edg€ case! " \\""'
        test_annotation = "this interval is for testing purposes only"

        expt_date1 = datetime.fromisoformat("2021-01-23 13:46:59")
        expt_date2 = datetime.fromisoformat("2021-01-24 02:00:43")
        expt_tags = [
            "shortTag",
            '"tag - with quotes"',
            '"\\nt3$T "edg€ case! "',
            '\\""',
        ]
        expt_annotation = "this interval is for testing purposes only"

        interval_str = "inc"
        assert as_interval(interval_str) == Interval()

        interval_str = "inc " + test_date1
        assert as_interval(interval_str) == Interval(start=expt_date1)

        interval_str = "inc # foo"
        assert as_interval(interval_str) == Interval(tags=["foo"])

        interval_str = "inc # " + test_tags
        assert as_interval(interval_str) == Interval(tags=expt_tags)

        interval_str = "inc # # " + test_annotation
        assert as_interval(interval_str) == Interval(annotation=expt_annotation)

        interval_str = "inc " + test_date1 + " - " + test_date2
        assert as_interval(interval_str) == Interval(start=expt_date1, end=expt_date2)

        interval_str = "inc " + test_date1 + " # " + "foo"
        assert as_interval(interval_str) == Interval(start=expt_date1, tags=["foo"])

        interval_str = "inc " + test_date1 + " # " + test_tags
        assert as_interval(interval_str) == Interval(start=expt_date1, tags=expt_tags)

        interval_str = "inc " + test_date1 + " # # " + test_annotation
        assert as_interval(interval_str) == Interval(
            start=expt_date1, annotation=expt_annotation
        )

        interval_str = "inc # " + "foo" + " # " + test_annotation
        assert as_interval(interval_str) == Interval(
            tags=["foo"], annotation=expt_annotation
        )

        interval_str = "inc # " + test_tags + " # " + test_annotation
        assert as_interval(interval_str) == Interval(
            tags=expt_tags, annotation=expt_annotation
        )

        interval_str = "inc " + test_date1 + " - " + test_date2 + " # " + "foo"
        assert as_interval(interval_str) == Interval(
            start=expt_date1, end=expt_date2, tags=["foo"]
        )

        interval_str = "inc " + test_date1 + " - " + test_date2 + " # " + test_tags
        assert as_interval(interval_str) == Interval(
            start=expt_date1, end=expt_date2, tags=expt_tags
        )

        interval_str = (
            "inc " + test_date1 + " - " + test_date2 + " # # " + test_annotation
        )
        assert as_interval(interval_str) == Interval(
            start=expt_date1, end=expt_date2, annotation=expt_annotation
        )

        interval_str = "inc " + test_date1 + " # " + "foo" + " # " + test_annotation
        assert as_interval(interval_str) == Interval(
            start=expt_date1, tags=["foo"], annotation=expt_annotation
        )

        interval_str = "inc " + test_date1 + " # " + test_tags + " # " + test_annotation
        assert as_interval(interval_str) == Interval(
            start=expt_date1, tags=expt_tags, annotation=expt_annotation
        )

        interval_str = (
            "inc "
            + test_date1
            + " - "
            + test_date2
            + " # "
            + "foo"
            + " # "
            + test_annotation
        )
        assert as_interval(interval_str) == Interval(
            start=expt_date1, end=expt_date2, tags=["foo"], annotation=expt_annotation
        )

        interval_str = (
            "inc "
            + test_date1
            + " - "
            + test_date2
            + " # "
            + test_tags
            + " # "
            + test_annotation
        )
        assert as_interval(interval_str) == Interval(
            start=expt_date1, end=expt_date2, tags=expt_tags, annotation=expt_annotation
        )

    def test_invalid_strings(self):
        """Test invalid interval strings."""
        with pytest.raises(RuntimeError):
            as_interval("")

        with pytest.raises(RuntimeError):
            as_interval("20210123T134659Z - 20210124T020043Z")

        with pytest.raises(RuntimeError):
            as_interval("dec # thisIsNoValidInterval")

        with pytest.raises(RuntimeError):
            as_interval("inc#thisIsNoValidInterval")

        with pytest.raises(RuntimeError):
            as_interval("inc\\n#\\nthisIsNoValidInterval")

        with pytest.raises(RuntimeError):
            as_interval("inc 1")


class TestTokenize:
    def test_empty(self):
        assert tokenize("") == []

    def test_single(self):
        assert tokenize("foo") == ["foo"]
        assert tokenize('"') == ['"']

    def test_multiple(self):
        assert tokenize("foo bar") == ["foo", "bar"]
        assert tokenize("foo-bar") == ["foo-bar"]
        assert tokenize("foo bar baz") == ["foo", "bar", "baz"]
        assert tokenize(" foo\nbar  \n baz") == ["foo", "bar", "baz"]

    def test_quotes_simple(self):
        with pytest.raises(AssertionError):
            assert tokenize("'foo bar'") == ["'foo bar'"]
        assert tokenize("'foo bar'") == ["'foo", "bar'"]
        assert tokenize('"foo"') == ['"foo"']
        assert tokenize('"foo bar baz"') == ['"foo bar baz"']
        assert tokenize('"foo bar" "baz"') == ['"foo bar"', '"baz"']
        assert tokenize('"foo" "bar baz"') == ['"foo"', '"bar baz"']

    def test_quotes_advanced(self):
        assert tokenize('""') == ['""']
        assert tokenize('" "') == ['" "']
        assert tokenize('" " "') == ['" "', '"']
        with pytest.raises(AssertionError):
            assert tokenize('" "foo"') == ['"', '"foo"']
        assert tokenize('" "foo"') == ['" "foo"']
        assert tokenize('"foo" "') == ['"foo"', '"']
        assert tokenize("\"foo' bar 'baz\"") == ["\"foo' bar 'baz\""]

    def test_real_example(self):
        test_date1 = "20210123T134659Z"
        test_date2 = "20210124T020043Z"
        test_tags = 'shortTag "tag - with quotes" "\\nt3$T "edg€ case! " \\""'
        test_annotation = "this interval is for testing purposes only"

        expt_date1 = [test_date1]
        expt_date2 = [test_date2]
        expt_tags = [
            "shortTag",
            '"tag - with quotes"',
            '"\\nt3$T "edg€ case! "',
            '\\""',
        ]
        expt_annotation = [
            "this",
            "interval",
            "is",
            "for",
            "testing",
            "purposes",
            "only",
        ]

        interval_str = (
            "inc "
            + test_date1
            + " - "
            + test_date2
            + " # "
            + test_tags
            + " # "
            + test_annotation
        )
        assert len(tokenize(interval_str)) == 17
        assert (
            tokenize(interval_str)
            == ["inc"]
            + expt_date1
            + ["-"]
            + expt_date2
            + ["#"]
            + expt_tags
            + ["#"]
            + expt_annotation
        )


class TestTokenizerNew:
    # 1. Tests which should succeed
    def test_standard_case(self):
        assert tokenize('abc def ghi') == ['abc', 'def', 'ghi']
        assert tokenize('"abc" "def" "ghi"') == ['"abc"', '"def"', '"ghi"']
        assert tokenize('"1bc" d2f "gh3"') == ['"1bc"', 'd2f', '"gh3"']
        assert tokenize('13* "4-5" 7/9') == ['13*', '"4-5"', '7/9']

    def test_special_tokens_acceptable(self):
        assert tokenize('"ghi" ') == ['"ghi"', '']

        # special cases with \ in the token
        # Note: \\ are to be read as \. \\ needs to be written for syntax reasons.
        assert tokenize('123 def "\\"" "ghi"') == ['123', 'def', '"\\""', '"ghi"'] # test for the token \"
        assert tokenize('\\ 123') == ['\\', '123'] # test for the token \
        assert tokenize('abc\\ def') == ['abc\\', 'def'] # test for unquoted tokens ending with \
        assert tokenize('"abc\\" efg" hij') == ['"abc\\" efg"', 'hij'] # test for quoted tokens ending in \
        assert tokenize('\\abc') == ['\\abc'] # test for \ before normal character

        # special cases with " in the token
        assert tokenize('abc"d"ef') == ['abc"d"ef'] # test for twice " in a token
        assert tokenize('abc"d') == ['abc"d']  # test for once " in a token
        assert tokenize('abc"d') == ['abc"d']  # test for " in the end of a token (interpreted as part of token, not as opening quotation mark)

        # other special cases
        assert tokenize('abc     def       ghi') == ['abc', 'def', 'ghi'] # test for skipping multiple whitespaces between tokens

    def test_special_tokens_inacceptable(self):
        with pytest.raises(Exception):
            tokenize('abc def \" ghi')     # test: a single " is not allowed as a token

        with pytest.raises(Exception):
            tokenize('"\\"')               # test: "\" is not allowed

        with pytest.raises(Exception):
            tokenize('"q1""q2"')           # test: whitespace missing between qouted tokens

        with pytest.raises(Exception):
            tokenize('"abc def')           # test: quotationmark missing
