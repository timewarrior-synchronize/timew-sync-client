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


import os
from typing import List


def write_data(interval_list: List[str]):
    """Writes the given interval list to files, separated by month and named accordingly.

    Writes each string to a separate file, named in accordance to its content,
    as specified by extract_file_name.

    Args:
        interval_list: A list of strings each of which contains all entries for one specific month.
    """
    data_folder = os.path.expanduser('~') + '/.timewarrior/data/'
    os.makedirs(data_folder, exist_ok=True)

    for month_data in interval_list:

        if len(month_data) == 0:
            return

        with open(data_folder + extract_file_name(month_data), 'w') as file:
            file.write(month_data)


def extract_file_name(month_data: str) -> str:
    """Returns the appropriate file name for the input provided.

    Analyses the provided input until the first line break is reached.
    Retrieves the month and year the entry has been recorded
    or is currently still being tracked.
    Further time intervals are expected to be in the same month
    and get transferred unchecked.

    Args:
        month_data: A string with time intervals in timewarrior format.

    Returns:
        A string containing the file name for the input provided.
    """
    assert len(month_data) >= 20
    if len(month_data) < 39:
        return month_data[4:8] + '-' + month_data[8:10] + '.data'
    else:
        return month_data[23:27] + '-' + month_data[27:29] + '.data'
