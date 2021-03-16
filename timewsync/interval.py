###############################################################################
#
# Copyright 2020 - 2021, 2021, Jan Bormet, Anna-Felicitas Hausmann, Joachim Schmidt, Vincent Stollenwerk, Arne Turuc
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


from __future__ import annotations

from datetime import datetime
from typing import List

from timewsync.tokenizer import tokenize

DATETIME_FORMAT = "%Y%m%dT%H%M%SZ"


class Interval:
    def __init__(
        self,
        start: datetime = None,
        end: datetime = None,
        tags: List[str] = None,
        annotation: str = None,
    ):
        if tags is None:
            tags = []
        self.start: datetime = start
        self.end: datetime = end
        self.tags: List[str] = tags
        self.annotation: str = annotation

    @classmethod
    def from_interval_str(cls, line: str) -> Interval:
        """Initialize object from interval string.

        Syntax (tokens separated by whitespace):
            'inc' [ <iso> [ '-' <iso> ]] [[ '#' <tag> [ <tag> ... ]] | [ '#' [ <tag> ... ] '#' <annotation> ]]

        Args:
            line: An interval string in correct syntax.

        Returns:
            A reference to the new Interval object.

        Raises:
            ValueError: The syntax has been violated
        """
        tokens = tokenize(line)

        # Required 'inc'
        if not tokens or tokens[0] != "inc":
            raise ValueError("unrecognizable line '%s'" % line)

        start = None
        end = None
        tags = []
        annotation = None
        cursor = 1

        # Optional <iso>
        if len(tokens) > 1 and len(tokens[1]) == 16:
            start = datetime.strptime(tokens[1], DATETIME_FORMAT)
            cursor = 2

            # Optional '-' <iso>
            if len(tokens) > 3 and tokens[2] == "-" and len(tokens[3]) == 16:
                end = datetime.strptime(tokens[3], DATETIME_FORMAT)
                cursor = 4

        # Optional '#'
        if len(tokens) > (cursor + 1) and tokens[cursor] == "#":

            # Optional <tag> ...
            tags = []
            cursor += 1
            while cursor < len(tokens) and tokens[cursor] != "#":
                tag = _strip_double_quotes(tokens[cursor])
                tags.append(tag)
                cursor += 1

            # Optional '#' <annotation>
            if cursor < len(tokens) and tokens[cursor] == "#":
                annotation = ""
                cursor += 1
                while cursor < len(tokens):
                    annotation += " " + tokens[cursor]
                    cursor += 1
                annotation = annotation.lstrip()[1:-1]

        # Unparsed tokens
        if cursor < len(tokens):
            raise ValueError("unrecognizable line '%s'" % line)

        return cls(
            start=start,
            end=end,
            tags=tags,
            annotation=annotation,
        )

    @classmethod
    def from_dict(cls, start: str = None, end: str = None, tags: List[str] = None, annotation: str = None) -> Interval:
        """Initialize object from dictionary.

        Args:
            start: (Optional) A date in DATETIME_FORMAT specifying the start of the interval.
            end: (Optional) A date in DATETIME_FORMAT specifying the end of the interval.
            tags: (Optional) A list of tags the interval contains.
            annotation: (Optional) The annotation of the interval.

        Returns:
            A reference to the new Interval object.
        """
        return cls(
            start=datetime.strptime(start, DATETIME_FORMAT) if start else None,
            end=datetime.strptime(end, DATETIME_FORMAT) if end else None,
            tags=tags,
            annotation=annotation,
        )

    def __eq__(self, other):
        """Check whether this object is equal to another one, by attributes."""
        if not isinstance(other, Interval):
            raise TypeError("can't compare %s with Interval" % type(other).__name__)
        return (
            self.start == other.start
            and self.end == other.end
            and self.tags == other.tags
            and self.annotation == other.annotation
        )

    def __str__(self) -> str:
        """Return the object as a string in timewarrior format."""
        out = "inc"
        if self.start:
            out += " " + self.start.strftime(DATETIME_FORMAT)
            if self.end:
                out += " - " + self.end.strftime(DATETIME_FORMAT)
        if self.tags:
            out += " #"
            for tag in self.tags:
                out += " " + _quote_tag_if_needed(tag)
        if self.annotation:
            if not self.tags:
                out += " #"
            out += f' # "{self.annotation}"'
        return out

    def asdict(self) -> dict:
        """Return the object as a dictionary."""
        return {
            "start": self.start.strftime(DATETIME_FORMAT) if self.start else "",
            "end": self.end.strftime(DATETIME_FORMAT) if self.end else "",
            "tags": self.tags,
            "annotation": self.annotation if self.annotation else "",
        }


def _strip_double_quotes(string: str) -> str:
    """Removes encapsulating double quotes, if there are some.

    Ignores non-encapsulating double quotes (one side only or inside).

    Args:
        string: The string to be pruned.

    Returns:
        The pruned string without encapsulating double quotes.
    """
    if not string or string == '""':
        return ""
    if len(string) >= 2 and string[0] == '"' and string[-1] == '"':
        return string[1:-1]
    return string


def _quote_tag_if_needed(tag: str) -> str:
    """Quotes tags just like timewarrior would quote them.

    Args:
        tag: The tag that should be quoted.

    Returns:
        The quoted tag.
    """
    if tag[0] == '"' or tag[0] == "'":
        return tag

    special_chars = [" ", '"', "+", "-", "/", "(", ")", "<", "^", "!", "=", "~", "_", "%"]

    if any(char in tag for char in special_chars):
        return f'"{tag}"'

    return tag
