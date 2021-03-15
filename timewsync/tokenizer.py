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


import enum
from typing import List


class State(enum.Enum):
    whitespace = enum.auto()  # read whitespaces between tokens
    simple_token = enum.auto()  # read unquoted token
    quoted_token = enum.auto()  # read quoted token
    quote_end = enum.auto()  # second quotation mark required to end quoted token
    escape_character = enum.auto()  # escape next character in quoted token
    error = enum.auto()  # invalid quotation syntax


def tokenize(line: str) -> List[str]:
    """Convert the input string into tokens, separated at whitespaces.

    A whitespace (or no character), followed by a double quote character ( ")
    is regarded as the beginning of a quoted substring.
    Quoted substrings are parsed as single tokens,
    which must end in another double quote character and separated to other tokens using whitespaces.

    Internally the input is read using a state machine.

    Args:
        line: The string input to be tokenized.

    Returns:
        A list of tokens.

    Raises:
        ValueError: The syntax described above has been violated
    """
    tokens = []
    state = State.whitespace
    current_token = -1  # index of current token

    for i, c in enumerate(line):

        # Whitespace state
        if state is State.whitespace:
            current_token = i
            if c == " ":
                continue
            elif c == '"':
                state = State.quoted_token
            else:
                state = State.simple_token

        # Simple Token state
        elif state is State.simple_token:
            if c == " ":
                state = State.whitespace
                tokens.append(line[current_token:i])
            else:
                continue

        # Quoted Token state
        elif state is State.quoted_token:
            if c == '"':
                state = State.quote_end
            elif c == "\\":
                state = State.escape_character
            else:
                continue

        # Quote End state
        elif state is State.quote_end:
            if c == " ":
                state = State.whitespace
                tokens.append(line[current_token:i])
            else:
                state = State.error

        # Escape Character state
        elif state is State.escape_character:
            state = State.quoted_token

        # Error state
        else:
            break

    # Potential last token
    if state in [State.simple_token, State.quoted_token, State.quote_end]:
        tokens.append(line[current_token:])

    # Accepting states
    if state in [State.whitespace, State.simple_token, State.quoted_token, State.quote_end]:
        return tokens

    # Non-accepting states
    raise ValueError("tokenization failed: '%s'" % line)
