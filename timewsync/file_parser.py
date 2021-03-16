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
from datetime import datetime
from typing import List, Dict

from timewsync import json_converter
from timewsync.interval import Interval


def as_interval_list(file_strings: Dict[str, str]) -> (List[Interval], Interval):
    """Converts a dictionary containing interval file strings into a list of Interval objects.

    Splits file strings at line breaks into separate intervals.
    Empty intervals are filtered out. Intervals being currently tracked are closed
    and re-opened as a new one, which is returned as the second argument.

    Args:
        file_strings: A dictionary containing the file names and corresponding file strings,
                      each of which containing intervals in timewarrior format.

    Returns:
        A list of Interval objects and a single Interval object, created if time tracking is active.
    """
    intervals = []
    active_interval = None
    for file_str in file_strings.values():
        for line in list(filter(None, file_str.splitlines())):  # Split and filter empty lines
            i = Interval.from_interval_str(line)
            if i.start:
                if not i.end:  # Split active time tracking, if present
                    i.end = datetime.utcnow()
                    active_interval = Interval(
                        start=i.end,
                        end=None,
                        tags=i.tags,
                        annotation=i.annotation,
                    )
                intervals.append(i)
    return intervals, active_interval


def as_file_strings(intervals: List[Interval], active_interval: Interval = None) -> (Dict[str, str], bool):
    """Converts a list of Interval objects into a dictionary containing interval file strings.

    Groups and sorts intervals per month and concatenates them using line breaks.
    Dictionary keys are file names and values corresponding file strings.
    If the second argument 'active_interval' is set and doesn't conflict
    with existing intervals, it is inserted as well and the method returns True.

    Args:
        intervals: A list of Interval objects.
        active_interval: (Optional) An Interval object being currently tracked.

    Returns:
        A dictionary containing the file names and corresponding file strings
        and a boolean value indicating whether time tracking is active.
    """
    intervals.sort(key=lambda i: i.start)

    if active_interval and not _conflicting(active_interval, intervals):
        intervals.append(active_interval)
        started_tracking = True
    else:
        started_tracking = False

    grouped_intervals = _group_by_month(intervals)
    file_strings = _join_per_group(grouped_intervals)

    return file_strings, started_tracking


def _conflicting(active_interval: Interval, sorted_intervals: List[Interval]) -> bool:
    """Returns true if open 'active_interval' overlaps with closed 'sorted_intervals'."""
    return sorted_intervals and sorted_intervals[-1].end > active_interval.start


def _group_by_month(intervals: List[Interval]) -> Dict[str, List[Interval]]:
    """Groups intervals per month and returns them as a dictionary.

    Dictionary keys are file names and values corresponding file strings.

    Args:
        intervals: A list of Interval objects.

    Returns:
        A dictionary containing the file names and corresponding interval lists per month.
    """
    grouped_intervals = defaultdict(list)
    for i in intervals:
        grouped_intervals[get_file_name(i)].append(i)
    return grouped_intervals


def _join_per_group(grouped_intervals: Dict[str, List[Interval]]) -> Dict[str, str]:
    """Concatenates grouped intervals per group by using line breaks.

    Args:
        grouped_intervals: A dictionary containing the file names and corresponding interval lists per group.

    Returns:
        A dictionary containing the file names and corresponding file strings per group.
    """
    file_strings = {}
    for file_name, intervals in grouped_intervals.items():
        file_str = [str(i) for i in intervals]
        file_strings[file_name] = "\n".join(file_str)
    return file_strings


def get_file_name(interval: Interval) -> str:
    """Returns the file name the Interval object should be stored in.

    Args:
        interval: The interval object to be classified

    Raises:
        ValueError: The interval does not have a start time
    """
    if not interval.start:
        raise ValueError("Missing start time in interval '%s'" % str(interval))
    return interval.start.strftime("%Y-%m.data")


def extract_tags(intervals: List[Interval]) -> str:
    """Extracts all tags and counts occurrences per tag.

    Returns one String containing every tag with how often it occurs.

    Args:
        intervals: A list of Interval objects.

    Returns:
        A string of all tags and the number of their occurrence written in the correct format for tags.data.
    """
    tags = defaultdict(int)
    for i in intervals:
        for tag in i.tags:
            tags[tag] += 1
    return json_converter.to_json_tags(tags)
