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


from typing import List


def to_interval_list(monthly_data: List[str]) -> List[str]:
    """Converts a list of monthly data into a list of intervals.

    Groups all intervals by month and concatenates them using line breaks.

    Args:
        monthly_data: A list of strings, each of which containing the data for one specific month.

    Returns:
        A list of time intervals in timewarrior format.
    """
    intervals = []
    for string in monthly_data:
        intervals += list(filter(None, string.splitlines()))
    return intervals


def to_monthly_data(intervals: List[str]) -> List[str]:
    """Converts a list of intervals into a list of monthly data.

    Groups all intervals by month and concatenates them using line breaks.

    Args:
        intervals: A list of time intervals in timewarrior format.

    Returns:
        A list of strings, each of which containing the data for one specific month.
    """
    monthly_data_dict = {}

    # Group all intervals by month
    for interval in intervals:
        file_name = extract_file_name(interval)
        if file_name in monthly_data_dict:
            monthly_data_dict[file_name].append(interval)
        else:
            monthly_data_dict[file_name] = [interval]

    monthly_data = []

    # Concatenate per month and fill monthly_data
    for entry in monthly_data_dict.values():
        # TODO sort lists
        month = '\n'.join(entry)
        monthly_data.append(month)

    return monthly_data


def extract_file_name(interval: str) -> str:
    """Returns the file name the interval should be stored in.

    Retrieves the month and year the interval has been recorded
    or is currently still being tracked.

    Args:
        interval: An interval string in timewarrior format.

    Returns:
        A string of the file name.
    """
    # TODO 'inc 20201214T134735Z # \"16-update-json-format\" \"thisIsATest\"' not working
    assert len(interval) >= 20
    if len(interval) < 39:
        return interval[4:8] + '-' + interval[8:10] + '.data'
    else:
        return interval[23:27] + '-' + interval[27:29] + '.data'


print(to_monthly_data(["inc 20201213T153500Z - 20201213T161247Z # \"QS1\"",
                 "inc 20201213T153500Z - 20201213T161247Z # QS2",
                 "inc 20210113T153500Z - 20210113T161247Z # QS3"]))
