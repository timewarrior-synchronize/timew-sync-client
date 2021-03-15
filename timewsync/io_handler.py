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


import os
import re
import tarfile
from pathlib import Path
from typing import Dict, Tuple, Optional

from jwcrypto.jwk import JWK

TIMEW_FOLDER = os.path.expanduser(os.environ.get("TIMEWARRIORDB", os.path.join("~", ".timewarrior")))
DATA_FOLDER = os.path.join(TIMEW_FOLDER, "data")


def read_data(timewsync_data_dir: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Reads the monthly separated interval data from timewarrior and the snapshot.

    Args:
        timewsync_data_dir: The timewsync data directory.

    Returns:
        A Tuple containing two lists of strings, holding the data for current and snapshot time intervals
        respectively, with each string containing the data for one month.
    """
    return _read_intervals(), _read_snapshot(timewsync_data_dir)


def _read_intervals() -> Dict[str, str]:
    """Reads the monthly separated interval data from timewarrior.

    Reads from all files matching 'YYYY-MM.data' and creates a separate list entry per month.

    Returns:
        A list of strings, each of which containing the data for one month.
    """
    monthly_data = {}

    if os.path.exists(DATA_FOLDER):

        # Identify all data sources
        file_list = [f for f in os.listdir(Path(DATA_FOLDER)) if (re.search(r"^\d\d\d\d-\d\d\.data$", f))]

        # Read all file contents
        for file_name in file_list:
            with open(os.path.join(DATA_FOLDER, file_name), "r") as file:
                monthly_data[file_name] = file.read()

    return monthly_data


def _read_snapshot(timewsync_data_dir: str) -> Dict[str, str]:
    """Reads the monthly separated interval data from the snapshot.

    Args:
        timewsync_data_dir: The timewsync data directory.

    Returns:
        A list of strings, each of which containing the data for one specific month.
    """
    snapshot_path = os.path.join(timewsync_data_dir, "snapshot.tgz")
    snapshot_data = {}

    # Open the snapshot and read all file contents
    if os.path.exists(snapshot_path):
        with tarfile.open(snapshot_path, mode="r:gz") as snapshot:
            for member in snapshot.getmembers():
                with snapshot.extractfile(member) as file:
                    file_data = file.read().decode("utf-8")
                    snapshot_data[member.name] = file_data

    return snapshot_data


def read_keys(timewsync_data_dir: str) -> Tuple[Optional[JWK], Optional[JWK]]:
    """Reads the private and the public key of the user.

    Args:
        timewsync_data_dir: The timewsync data directory.

    Returns:
        Two strings containing the private and the public key of the user.
        If the keys don't exist, return None.
    """
    priv_pem = None
    pub_pem = None

    priv_pem_path = os.path.join(timewsync_data_dir, "private_key.pem")
    pub_pem_path = os.path.join(timewsync_data_dir, "public_key.pem")

    if os.path.exists(priv_pem_path):
        with open(priv_pem_path, "rb") as file:
            priv_pem = file.read()

    if os.path.exists(pub_pem_path):
        with open(pub_pem_path, "rb") as file:
            pub_pem = file.read()

    private_key = JWK.from_pem(priv_pem) if priv_pem else None
    public_key = JWK.from_pem(pub_pem) if pub_pem else None

    return private_key, public_key


def write_data(timewsync_data_dir: str, monthly_data: Dict[str, str], tags: str):
    """Writes the monthly separated data to files in .timewarrior/data.

    Args:
        timewsync_data_dir: The timewsync data directory.
        monthly_data: A dictionary containing the file names and corresponding data for every month.
        tags: A string of tags and how often they have occurred, in the final format.
    """
    _write_intervals(monthly_data)
    _write_snapshot(timewsync_data_dir, monthly_data)
    _write_tags(tags)


def _write_intervals(monthly_data: Dict[str, str]):
    """Writes the monthly separated data to files, which are named accordingly.

    Args:
        monthly_data: A dictionary containing the file names and corresponding data for every month.
    """
    # Find data directory, create if not present
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Write data to files
    for file_name, data in monthly_data.items():
        with open(os.path.join(DATA_FOLDER, file_name), "w") as file:
            file.write(data)


def _write_snapshot(timewsync_data_dir: str, monthly_data: Dict[str, str]) -> None:
    """Creates a backup of the written files as a tar archive in gz compression.

    Takes the file name specified in the timewsync config, defaults to 'snapshot.tgz'.

    Args:
        timewsync_data_dir: The timewsync data directory.
        monthly_data: A dictionary containing the file names and corresponding data for every month.
    """
    # Find timewsync data directory, create if not present
    os.makedirs(timewsync_data_dir, exist_ok=True)

    snapshot_path = os.path.join(timewsync_data_dir, "snapshot.tgz")

    # Write data to files in snapshot
    with tarfile.open(snapshot_path, mode="w:gz") as snapshot:
        for file_name in monthly_data.keys():
            snapshot.add(os.path.join(DATA_FOLDER, file_name), arcname=file_name)


def _write_tags(tags: str) -> None:
    """Overrides tags.data.

    Gets one String in the correct format for tags.data and writes it to tags.data.
    Whatever was before in tags.data will be overwritten.
    tags.data will be created if it has not been there before.

    Args:
        tags: A string of tags and how often they have occurred, in the final format.

    Returns:
        Does not return; just writes into file.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(os.path.join(DATA_FOLDER, "tags.data"), "w") as file:
        file.write(tags)


def write_keys(timewsync_data_dir: str, priv_pem: bytes, pub_pem: bytes) -> None:
    """Overrides the key files.

    Args:
        timewsync_data_dir: The path to the timewsync directory.
        priv_pem: The private key in PEM format.
        pub_pem: The public key in PEM format.
    """
    os.makedirs(timewsync_data_dir, exist_ok=True)

    with open(os.path.join(timewsync_data_dir, "private_key.pem"), "wb") as file:
        file.write(priv_pem)

    with open(os.path.join(timewsync_data_dir, "public_key.pem"), "wb") as file:
        file.write(pub_pem)


def delete_snapshot(timewsync_data_dir: str) -> None:
    """Deletes the current snapshot in the timewsync data directory. Use
    in case of emergency (when writing new interval data to disk fails)

    Args:
        timewsync_data_dir: The timewsync data directory.
    """
    snapshot_path = os.path.join(timewsync_data_dir, "snapshot.tgz")

    # Delete snapshot
    if os.path.isfile(snapshot_path):
        os.remove(snapshot_path)
