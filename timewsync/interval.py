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
    def from_interval_str(cls):
        """Initialize object from interval string."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, interval_dict: dict):
        """Initialize object from dictionary."""
        return cls(
            start=datetime.strptime(interval_dict["start"], DATETIME_FORMAT)
            if "start" in interval_dict
            else None,
            end=datetime.strptime(interval_dict["end"], DATETIME_FORMAT)
            if "end" in interval_dict
            else None,
            tags=interval_dict["tags"] if "tags" in interval_dict else [],
            annotation=interval_dict["annotation"]
            if "annotation" in interval_dict
            else None,
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
                out += " " + tag
        if self.annotation:
            if not self.tags:
                out += " #"
            out += " # " + self.annotation
        return out

    def asdict(self) -> dict:
        """Return the object as a dictionary."""
        return {
            "start": self.start.strftime(DATETIME_FORMAT) if self.start else "",
            "end": self.end.strftime(DATETIME_FORMAT) if self.end else "",
            "tags": self.tags,
            "annotation": self.annotation if self.annotation else "",
        }


def as_interval(line: str) -> Interval:
    """Parse an Interval from the provided string.

    Syntax (tokens separated by whitespace):
        'inc' [ <iso> [ '-' <iso> ]] [[ '#' <tag> [ <tag> ... ]] | [ '#' [ <tag> ... ] '#' <annotation> ]]

    Args:
        line: An interval string in correct syntax.

    Returns:
        The same interval parsed to an Interval object.
    """
    tokens = tokenize(line)

    # Required 'inc'
    if not tokens or tokens[0] != "inc":
        raise RuntimeError("unrecognizable line '%s'" % line)
    interval = Interval()
    cursor = 1

    # Optional <iso>
    if len(tokens) > 1 and len(tokens[1]) == 16:
        interval.start = datetime.strptime(tokens[1], DATETIME_FORMAT)
        cursor = 2

        # Optional '-' <iso>
        if len(tokens) > 3 and tokens[2] == "-" and len(tokens[3]) == 16:
            interval.end = datetime.strptime(tokens[3], DATETIME_FORMAT)
            cursor = 4

    # Optional '#'
    if len(tokens) > (cursor + 1) and tokens[cursor] == "#":

        # Optional <tag> ...
        interval.tags = []
        cursor += 1
        while cursor < len(tokens) and tokens[cursor] != "#":
            interval.tags.append(tokens[cursor])
            cursor += 1

        # Optional '#' <annotation>
        if cursor < len(tokens) and tokens[cursor] == "#":
            annotation = ""
            cursor += 1
            while cursor < len(tokens):
                annotation += " " + tokens[cursor]
                cursor += 1
            interval.annotation = annotation.lstrip()

    # Unparsed tokens
    if cursor < len(tokens):
        raise RuntimeError("unrecognizable line '%s'" % line)

    return interval
