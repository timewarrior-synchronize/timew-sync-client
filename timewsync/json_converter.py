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


from collections import defaultdict
from typing import List, Tuple, Dict
import json

from timewsync.interval import Interval


def to_json_request(user_id: int, diff: Tuple[List[Interval], List[Interval]]) -> str:
    """Build and return a JSON string using the diff provided.

    The diff must contain a list of added and a list of removed Interval objects.

    Args:
        user_id: The identification number of the current user.
        diff: A Tuple of added and removed Interval objects.

    Returns:
        A JSON string containing the user id and lists of added and removed Interval objects.
    """
    added_dict = [interval.asdict() for interval in diff[0]]
    removed_dict = [interval.asdict() for interval in diff[1]]
    json_dict = {
        "userID": user_id,
        "added": added_dict,
        "removed": removed_dict,
    }
    return json.dumps(json_dict)


def from_json_response(json_str: str) -> (List[Interval], bool):
    """Extract and return a list of Interval objects from the given JSON response.

    Args:
        json_str: A JSON string containing a list of Interval objects.

    Returns:
        A list of Interval objects and a boolean flag indicating whether a conflict had been resolved.
    """
    json_dict = json.loads(json_str)
    intervals = [Interval.from_dict(**interval_dict) for interval_dict in json_dict["intervals"]]
    conflict_flag = json_dict["conflictsOccurred"]
    return intervals, conflict_flag


def to_json_tags(tags: Dict[str, int]) -> str:
    """Converts a dictionary holding tags and occurrences into a single JSON string."""
    file_str = defaultdict(dict)
    for tag, count in tags.items():
        tag = tag.replace('\\"', '"')
        file_str[tag] = {"count": count}
    return json.dumps(file_str, indent=2)


def from_json_error_response(json_str: str) -> (str, str):
    """Extract message and details from a JSON error response

    Args:
        json_str: A JSON string containing the verbatim error response from the server

    Returns:
        A tuple containing the error message and technical details
    """
    json_dict = json.loads(json_str)
    message = json_dict["message"]
    details = json_dict["details"]

    return message, details
