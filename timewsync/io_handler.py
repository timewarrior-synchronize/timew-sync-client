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
from typing import List, Dict, Tuple

TIMEW_FOLDER = os.path.expanduser(os.environ.get('TIMEWARRIORDB', os.path.join('~', '.timewarrior')))
DATA_FOLDER = os.path.join(TIMEW_FOLDER, 'data')


def read_data(timewsync_data_dir: str) -> Tuple[List[str], List[str]]:
    """Reads the monthly separated interval data from timewarrior and the snapshot."""
    return read_intervals(), read_snapshot(timewsync_data_dir)


def read_intervals() -> List[str]:
    """Reads the monthly separated interval data from timewarrior.

    Reads from all files matching 'YYYY-MM.data' and creates a separate list entry per month.

    Returns:
        A list of strings, each of which containing the data for one month.
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


def read_snapshot(timewsync_data_dir: str) -> List[str]:
    """Reads the monthly separated interval data from the snapshot.

    Args:
        timewsync_data_dir: The timewsync data directory.

    Returns:
        A list of strings, each of which containing the data for one specific month.
    """
    snapshot_path = os.path.join(timewsync_data_dir, 'snapshot.tgz')
    snapshot_data = []

    # Open the snapshot and read all file contents
    if os.path.exists(snapshot_path):
        with tarfile.open(snapshot_path, mode='r:gz') as snapshot:
            for member in snapshot.getmembers():
                with snapshot.extractfile(member) as file:
                    file_data = file.read().decode('utf-8')
                    snapshot_data.append(file_data)

    return snapshot_data


def write_data(timewsync_data_dir: str, monthly_data: Dict[str, str], tags: str):
    """Writes the monthly separated data to files in .timewarrior/data.

    Args:
        timewsync_data_dir: The timewsync data directory.
        monthly_data: A dictionary containing the file names and corresponding data for every month.
        tags: A string of tags and how often they have occurred, in the final format.
    """
    write_intervals(monthly_data)
    write_snapshot(timewsync_data_dir, monthly_data)
    write_tags(tags)


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


def write_snapshot(timewsync_data_dir: str, monthly_data: Dict[str, str]):
    """Creates a backup of the written files as a tar archive in gz compression.

    Takes the file name specified in the timewsync config, defaults to 'snapshot.tgz'.

    Args:
        timewsync_data_dir: The timewsync data directory.
        monthly_data: A dictionary containing the file names and corresponding data for every month.
    """
    # Find timewsync data directory, create if not present
    os.makedirs(timewsync_data_dir, exist_ok=True)

    snapshot_path = os.path.join(timewsync_data_dir, 'snapshot.tgz')

    # Write data to files in snapshot
    with tarfile.open(snapshot_path, mode='w:gz') as snapshot:
        for file_name in monthly_data.keys():
            snapshot.add(os.path.join(DATA_FOLDER, file_name), arcname=file_name)


def write_tags(tags: str) -> None:
    """
        Gets one String in the correct format for tags.data and writes it to tags.data .
        Whatever was before in tags.data will be overwritten.
        tags.data will be created if it has not been there before.

    :param tags: A string of tags and how often they have occurred, in the final format.
    :return: Does not return; just writes into file.
    """

    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(DATA_FOLDER + 'tags.data', 'w') as file:
        file.write(tags)
