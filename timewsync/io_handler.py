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
import tarfile
from pathlib import Path
from typing import List, Dict

TIMEW_FOLDER = os.path.expanduser(os.environ.get('TIMEWARRIORDB', os.path.join('~', '.timewarrior')))
DATA_FOLDER = os.path.join(TIMEW_FOLDER, 'data')


def read_data() -> List[str]:
    """Reads the monthly separated time intervals from .timewarrior/data into a single list.

    Reads from all files matching 'YYYY-MM.data' and creates a separate list entry per month.

    Returns:
        A list of strings, each of which containing the data for one specific month.
    """
    monthly_data = []

    # Filter and list all data sources
    if os.path.exists(DATA_FOLDER):
        file_list = [f for f in os.listdir(Path(DATA_FOLDER)) if (re.search(r'^\d\d\d\d-\d\d\.data$', f))]

        # Read all file contents
        for file_name in file_list:
            with open(os.path.join(DATA_FOLDER, file_name), 'r') as file:
                monthly_data.append(file.read())

    return monthly_data


def write_data(monthly_data: Dict[str, str], timewsync_data_dir: str):
    """Writes the monthly separated data to files in .timewarrior/data.

    Args:
        monthly_data: A dictionary containing the file names and corresponding data for every month.
        timewsync_data_dir: The timewsync data directory
    """
    write_intervals(monthly_data)
    write_snapshot(monthly_data, timewsync_data_dir)


def write_intervals(monthly_data: Dict[str, str]):
    """Writes the monthly separated data to files, which are named accordingly.

    Args:
        monthly_data: A dictionary containing the file names and corresponding data for every month.
    """
    # Find data directory, create if not present
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Write data to files
    for file_name, data in monthly_data.items():
        with open(os.path.join(DATA_FOLDER, file_name), 'w') as file:
            file.write(data)


def write_snapshot(monthly_data: Dict[str, str], timewsync_data_dir: str):
    """Creates a backup of the written files as a tar archive in gz compression.

    Takes the file name specified in the timewsync config, defaults to 'snapshot.tgz'.

    Args:
        monthly_data: A dictionary containing the file names and corresponding data for every month.
        timewsync_data_dir: The timewsync data directory
    """
    # Find timewsync data directory, create if not present
    os.makedirs(timewsync_data_dir, exist_ok=True)

    snapshot_path = os.path.join(timewsync_data_dir, 'snapshot.tgz')

    with tarfile.open(snapshot_path, mode='w:gz') as snapshot:
        for file_name in monthly_data.keys():
            snapshot.add(os.path.join(DATA_FOLDER, file_name), arcname=file_name)
