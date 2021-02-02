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
import enum

DATETIME_FORMAT = '%Y%m%dT%H%M%SZ'


class Interval:

    def __init__(self, start: datetime = None, end: datetime = None, tags: List[str] = None, annotation: str = None):
        if tags is None:
            tags = []
        self.start: datetime = start
        self.end: datetime = end
        self.tags: List[str] = tags
        self.annotation: str = annotation

    def __eq__(self, other):
        """Checks whether this object is equal to another one, by attributes."""
        if not isinstance(other, Interval):
            raise TypeError('can\'t compare %s with Interval' % type(other).__name__)
        return self.start == other.start and self.end == other.end and self.tags == other.tags and self.annotation == other.annotation

    def __str__(self) -> str:
        """Returns the interval as a string in timewarrior format."""
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
        'inc' [ <iso> [ '-' <iso> ]] [[ '#' <tag> [ <tag> ... ]] | [ '#' [ <tag> ... ] '#' <annotation> ]]

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
    cursor = 1

    # Optional <iso>
    if len(tokens) > 1 and len(tokens[1]) == 16:
        interval.start = datetime.strptime(tokens[1], DATETIME_FORMAT)
        cursor = 2

        # Optional '-' <iso>
        if len(tokens) > 3 and tokens[2] == '-' and len(tokens[3]) == 16:
            interval.end = datetime.strptime(tokens[3], DATETIME_FORMAT)
            cursor = 4

    # Optional '#'
    if len(tokens) > (cursor + 1) and tokens[cursor] == '#':

        # Optional <tag> ...
        interval.tags = []
        cursor += 1
        while cursor < len(tokens) and tokens[cursor] != '#':
            interval.tags.append(tokens[cursor])
            cursor += 1

        # Optional '#' <annotation>
        if cursor < len(tokens) and tokens[cursor] == '#':
            annotation = ''
            cursor += 1
            while cursor < len(tokens):
                annotation += ' ' + tokens[cursor]
                cursor += 1
            interval.annotation = annotation.lstrip()

    # Unparsed tokens
    if cursor < len(tokens):
        raise RuntimeError('unrecognizable line \'%s\'' % line)

    return interval

class State(enum.Enum):
    start = 0
    normal = 1
    firstquote = 2
    quotestate = 3
    escape = 4
    secondquote = 5


def tokenize(string: str) -> List[str]:
    """Converts the input string into tokens, separated at whitespaces.
    Correctly handles quoted strings.
    Returns an error if the string contains trailing whitespace or quotationmarks without leading whitespace.

    Args:
        string: The string input to be tokenized.

    Returns:
        A list of tokens.
    """

    # The logic of this function is based on a DFA (definite final automat). In state, the state of the automat will be stored.
    state = State.start
    result = []         # will be the list of tokens
    start_of_token = 0
    i = 0               # pointer: index where the loop is operating on the string

    # Iterate through string, characterwise
    for c in string:

        print("1: I am in " + str(state) + " ; and I read a " + c)

        if state == State.start:
            if c == '"':        # tags starts with quote
                state = State.firstquote
                print ("2: I get to firstquote state.")
            elif c == ' ':       # There may be as many whitespaces between tags, they shall be skipped.
                start_of_token = i+1
                print("2b: I set pointer anew." + "\n")
            else:               # tag does not start with quote
                state = State.normal
                print ("3: I get to normal state.")

        elif state == State.normal:
            if c == ' ':    # whitespace ends any tag which is not in quotes
                result.append(string[start_of_token:i])
                state = State.start
                print ("4: I get to start state.")
                start_of_token = i+1    # TODO: could cause trouble? || Is writing implemented well and correctly?
                print("5: I read " + result[-1] + " in state normal." + "\n")
            else:
                pass        # All other characters, including \ and ", are normal characters in a non-quoted tag. They shall be read.

        elif state == State.firstquote:
            if c == '\\':    # \ in qouted tags are used to escape the following character. This is a check for a single \. It's written \\ only due to python syntax.
                state = State.escape
                print ("6: I get to escape state.")
            elif c == '"':
            # TODO firstquote mit elif: geht; mit if: geht nicht!
                state = State.secondquote   # a second quote does end any tag which started with a quote
                print ("7: I get to 2ndquote state.")
            else:
                state = State.quotestate    # Any other character is a normal character. It shall be read.
                print ("8: I get to quotestate.")

        elif state == State.quotestate:
            if c == "\\":   # \ in qouted tags are used to escape the following character.
                            # This is a check for a single \. It's written \\ only due to python syntax.
                state = State.escape
                print ("9: I get to escape state.")
            elif c == '"':
                state = State.secondquote   # a second quote does end any tag which started with a quote
                print ("10: I get to 2ndquote state.")
            else:
                pass                        # Any other character is a normal character. It shall be read.

        elif state == State.secondquote:
            if c == ' ':    # after a qouted tag, a whitespace or the end of the string must follow.
                result.append(string[start_of_token:i])
                state = State.start
                print ("11: I get to start state.")
                start_of_token = i+1    # TODO: could cause trouble? || Is writing implemented well and correctly?
                print("12: I read " + result[-1] + " in state secondquote." + "\n")
            else:
                raise Exception("13: Whitespace missing after tag surrounded by quotes.")
                return None

        elif state == State.escape:
            print("14: I'm in escape state.")
            state = State.quotestate
            print ("I get to quotestate.")

        i += 1
    print("15: Ende: " + str(state), c)
    if ((state != State.start) and (state != State.normal) and (state != State.secondquote)):
        raise Exception("Found single quotation mark.")
        return None
    else:
        result.append(string[start_of_token:])
        return result

# \\ always has python-syntax reasons. They are to be read as \
# print((tokenize('abc def \" ghi'))) # shall throw error because a single " is not allowed
#print((tokenize("abc def ghi")))    # standard case with only tgas without quotes
#print((tokenize('123 def "\\"" "ghi" '))) # to be read as \" sorrounded by "...". For syntactical reasons, \\ must be written.
#print((tokenize('abc"d"ef')))
# print((tokenize('abc\\'))) # geht, soll gehen
# print((tokenize('"abc\\" efg"'))) # geht, soll gehen
# print((tokenize('"\\""'))) # geht, soll gehen
# print((tokenize('"\\""'))) # geht, soll gehen
# print((tokenize('abc     def       ghi'))) # geht, soll whitespaces zwischen tags skippen
# print((tokenize('\abc'))) # soll gehen TODO: Achtung, es gibt ['\x07bc'] zurück!
#print(tokenize('\\')) # geht, soll gehen
print((tokenize('abc"d')))  # geht, soll gehen


# sollen nicht gehen
# print((tokenize('"\\"')))
# print((tokenize('"')))  # geht nicht, soll nicht gehen
# print((tokenize('"q1""q2')))  # geht nicht, soll nicht gehen, missing whitespace
print((tokenize('"abc def')))  # missing closing quotationmark
print((tokenize('abc def"')))  # missing closing quotationmark


