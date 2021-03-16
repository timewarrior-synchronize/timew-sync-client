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


import pytest

from timewsync.tokenizer import tokenize


class TestTokenize:
    def test_empty(self):
        """Test with empty input."""
        assert tokenize("") == []  # no tokens
        assert tokenize(" ") == []  # no tokens

    def test_single(self):
        """Test with one token."""
        assert tokenize("a") == ["a"]  # single character
        assert tokenize("foo") == ["foo"]  # single word
        assert tokenize('"') == ['"']  # valid per timewarrior implementation

    def test_multiple(self):
        """Test with multiple tokens."""
        assert tokenize("foo bar") == ["foo", "bar"]  # whitespace separates
        assert tokenize("foo-bar") == ["foo-bar"]  # non-whitespace doesn't separate
        assert tokenize("foo bar baz") == ["foo", "bar", "baz"]  # simple boundary check
        assert tokenize(" foo bar   baz  ") == [
            "foo",
            "bar",
            "baz",
        ]  # advanced boundary check
        assert tokenize("-1 0 1") == ["-1", "0", "1"]  # numbers check
        assert tokenize("$13 4.5 7/9%") == [
            "$13",
            "4.5",
            "7/9%",
        ]  # numbers with characters
        assert tokenize("foo\\ \\bar") == [
            "foo\\",
            "\\bar",
        ]  # unquoted escape character is not functional

    def test_quotes_simple(self):
        """Tests with simple quoted substrings."""
        with pytest.raises(AssertionError):
            assert tokenize("'foo bar'") == ["'foo bar'"]  # single quotes do not qualify
        assert tokenize("'foo bar'") == [
            "'foo",
            "bar'",
        ]  # single quotes treated as normal character
        assert tokenize('""') == ['""']  # double quotes without content
        assert tokenize('" "') == ['" "']  # double quoted whitespace
        assert tokenize('"foo"') == ['"foo"']  # double quoted text
        assert tokenize('"foo bar"') == ['"foo bar"']  # double quoted text treated as single token
        assert tokenize('"foo bar baz"') == ['"foo bar baz"']  # quote check 1
        assert tokenize('"foo bar" "baz"') == ['"foo bar"', '"baz"']  # quote check 2
        assert tokenize('"foo" "bar baz"') == ['"foo"', '"bar baz"']  # quote check 3
        assert tokenize('"foo" "bar" "baz"') == [
            '"foo"',
            '"bar"',
            '"baz"',
        ]  # quote check 4
        assert tokenize('"1oo" b4r "ba2"') == [
            '"1oo"',
            "b4r",
            '"ba2"',
        ]  # numbers with/without quotes

    def test_quotes_advanced(self):
        """Tests with advanced quoted substrings and edge cases."""
        assert tokenize('fo" b"r') == [
            'fo"',
            'b"r',
        ]  # double quotes with leading non-whitespace don't qualify
        assert tokenize('\\ "\\"" "\\\\\\""') == [
            "\\",
            '"\\""',
            '"\\\\\\""',
        ]  # escape characters in quotes functional

        assert tokenize('" " "') == ['" "', '"']  # earliest pair is taken
        assert tokenize('"foo') == ['"foo']  # no closing quotation mark at eos allowed
        assert tokenize('"\\"') == ['"\\"']  # no closing quotation mark at eos allowed

        with pytest.raises(ValueError):
            tokenize('"\\\\""')  # whitespace separator missing
        with pytest.raises(ValueError):
            tokenize('"foo"bar')  # whitespace separator missing
        with pytest.raises(ValueError):
            tokenize('"foo""bar"')  # whitespace separator missing
