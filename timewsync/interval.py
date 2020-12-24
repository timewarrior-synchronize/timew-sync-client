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

DATETIME_FORMAT = '%Y%m%dT%H%M%SZ'


class Interval:

    def __init__(self, start: datetime = None, end: datetime = None, tags: List[str] = None, annotation: str = None):
        self.start: datetime = start
        self.end: datetime = end
        self.tags: List[str] = tags
        self.annotation: str = annotation

    def __str__(self) -> str:
        """Returns the interval as a string."""
        out = 'inc'
        if self.start:
            out += ' ' + self.start.strftime(DATETIME_FORMAT)
            if self.end:
                out += ' - ' + self.end.strftime(DATETIME_FORMAT)
        if self.tags:
            out += ' #'
            for tag in self.tags:
                out += ' ' + tag
        if self.annotation:
            if not self.tags:
                out += ' #'
            out += ' # ' + self.annotation
        return out


def as_interval(line: str) -> Interval:
    """Parses an Interval from the provided string.

    Syntax (tokens separated by whitespace):
        'inc' [ <iso> [ '-' <iso> ]] [ '#' [ <tag> [ <tag> ... ]] [ '#' <annotation> ]]

    Args:
        line: An interval string in correct syntax.

    Returns:
        The same interval parsed to an Interval object.
    """
    tokens = tokenize(line)

    # Required 'inc'
    if not tokens or tokens[0] != 'inc':
        raise RuntimeError('unrecognizable line \'%s\'' % line)
    interval = Interval()
    offset = 0

    # Optional <iso>
    if len(tokens) > 1 and len(tokens[1]) == 16:
        interval.start = datetime.strptime(tokens[1], DATETIME_FORMAT)
        offset = 1

        # Optional '-' <iso>
        if len(tokens) > 3 and tokens[2] == '-' and len(tokens[3]) == 16:
            interval.end = datetime.strptime(tokens[3], DATETIME_FORMAT)
            offset = 3

    # Optional '#'
    if len(tokens) > 2 + offset and tokens[1 + offset] == '#':

        # Optional <tag> ...
        interval.tags = []
        index = 2 + offset
        while index < len(tokens) and tokens[index] != '#':
            interval.tags.append(tokens[index])
            index += 1

        # Optional '#' <annotation>
        if index < len(tokens) and tokens[index] == '#':
            annotation = ''
            for i in range(index + 1, len(tokens)):
                annotation += ' ' + tokens[i]
            interval.annotation = annotation.lstrip()

    return interval


def tokenize(line: str) -> List[str]:
    """Converts the input string into tokens.

    Tokens are split at any whitespace and in string format.
    Recognizes double quoted sentences as one token.

    Args:
        line: The string input to be tokenized.

    Returns:
        A list of tokens based on the string.
    """
    line = ' ' + line + ' '
    eos = len(line)
    tokens = []
    start = 0

    while start < eos:
        mid = line.find(' "', start)
        end = line.find('" ', mid+2)

        if mid == -1 or end == -1:
            tokens += line[start:].split()
            start = eos
        else:
            tokens += line[start:mid].split()
            tokens += [line[mid+1:end+1]]
            start = end + 1

    return tokens
