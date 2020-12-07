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


def read_data():
    """Return a list of strings each of which containing all lines from a single monthly file in .timewarrior/data."""
    # Navigate to .home/.timewarrior/data
    data_folder = Path(os.path.expanduser('~') + "/.timewarrior/data")
    # Make a list from all .data files you shall read
    file_list = [f for f in os.listdir(data_folder) if (re.search('\d\d\d\d-\d\d.data', f))]
    # Iterate over the list and read each file (= month). Write the content of each file into a list of strings: one string for each file.
    return [(open(os.path.expanduser('~') + "/.timewarrior/data/" + file).read()) for file in file_list]
