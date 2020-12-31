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


from typing import List, Dict

from timewsync.interval import Interval, as_interval


def to_interval_list(monthly_data: List[str]) -> List[Interval]:
    """Converts a list of monthly data into a list of Interval objects.

    Splits the monthly i strings into separate intervals at line breaks.
    Empty intervals are filtered out.

    Args:
        monthly_data: A list of strings, each of which containing the data for one specific month.

    Returns:
        A list of Interval objects.
    """
    intervals = []
    for month in monthly_data:
        for line in month.splitlines():
            if line:
                intervals.append(as_interval(line))
    return intervals


def to_monthly_data(intervals: List[Interval]) -> Dict[str, str]:
    """Converts a list of Interval objects into a string dictionary.

    Groups all intervals by month and concatenates them using line breaks.
    Keys are the file names the values' data should be stored in.

    Args:
        intervals: A list of Interval objects.

    Returns:
        A dictionary containing the file names and corresponding data for every month.
    """
    grouped_intervals_dict = {}

    # Group all intervals by month
    for interval in intervals:
        file_name = get_file_name(interval)
        if file_name in grouped_intervals_dict:
            grouped_intervals_dict[file_name].append(interval)
        else:
            grouped_intervals_dict[file_name] = [interval]

    monthly_data_dict = {}

    # Sort and concatenate all intervals per month
    for file_name, month in grouped_intervals_dict.items():
        month.sort(key=lambda i: i.start)
        monthly_data_dict[file_name] = '\n'.join(str(month))

    return monthly_data_dict


def get_file_name(interval: Interval) -> str:
    """Returns the file name the i should be stored in."""
    if not interval.start:
        raise RuntimeError('corrupt interval \'%s\'' % str(interval))
    return interval.start.strftime('%Y-%m.data')
