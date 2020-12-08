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
import re
from pathlib import Path
from typing import List


def read_data() -> List[str]:
    """Reads the monthly separated time intervals from .timewarrior/data into one string list.

    Reads from all files matching 'YYYY-MM.data' and creates a separate list entry per month.

    Returns:
        A list of strings each of which contains all entries for one specific month.
    """
    # Filter and list all data sources
    data_folder = os.path.expanduser('~') + '/.timewarrior/data/'
    file_list = [f for f in os.listdir(Path(data_folder)) if (re.search(r'^\d\d\d\d-\d\d\.data$', f))]

    # Read file contents into interval list
    interval_list = []
    for file_name in file_list:
        with open(data_folder + file_name, 'r') as file:
            interval_list.append(file.read())

    return interval_list
