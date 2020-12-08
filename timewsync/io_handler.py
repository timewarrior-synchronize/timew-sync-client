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
    """Write the given data to files, separated by month and named accordingly."""
    data_folder = os.path.expanduser('~') + '/.timewarrior/data/'

    for month_data in interval_list:

        if len(month_data) == 0:
            return

        file = open(data_folder + extract_file_name(month_data), 'w')
        file.write(month_data)
        file.close()


def extract_file_name(month_data: str) -> str:
    """Return the new filename in which the new data should be stored, based on the first line of the content provided."""
    assert len(month_data) >= 20
    if len(month_data) < 39:
        return month_data[4:8] + '-' + month_data[8:10] + '.data'
    else:
        return month_data[23:27] + '-' + month_data[27:29] + '.data'
