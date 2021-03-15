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
from typing import List, Tuple
from urllib.parse import urljoin

import requests

from timewsync import json_converter
from timewsync.interval import Interval
from timewsync.config import Configuration

SYNC_ENDPOINT = "/api/sync"


class ServerError(Exception):
    """Error response from the synchronization server

    Attributes:
        status_code: HTTP status code reported by the server
        message: Error message sent by server
        details: Additional technical details reported by the server
    """

    def __init__(self, status_code: int, message: str, details: str):
        self.status_code: int = status_code
        self.message: str = message
        self.details: str = details


def dispatch(
    config: Configuration, timew_intervals: List[Interval], snapshot_intervals: List[Interval], auth_token: str
) -> (List[Interval], bool):
    """Send a sync request to the server.

    Args:
        config: The timewsync configuration file.
        timew_intervals: A list of all client Interval objects.
        snapshot_intervals: A list of all Interval objects found in the snapshot of the latest sync.
        auth_token: A JWT used as authentication token.

    Returns:
        A list of Interval objects resulting from the sync
        and a boolean flag indicating whether a conflict had been resolved.
    """
    diff = generate_diff(timew_intervals, snapshot_intervals)

    request_url = urljoin(config.server_base_url, SYNC_ENDPOINT)
    request_body = json_converter.to_json_request(config.user_id, diff)

    header = {"Authorization": f"Bearer {auth_token}"}

    server_response = requests.put(request_url, request_body, headers=header)

    if server_response.status_code != 200:
        message, details = json_converter.from_json_error_response(server_response.text)
        raise ServerError(server_response.status_code, message, details)

    parsed_response, conflict_flag = json_converter.from_json_response(server_response.text)

    return parsed_response, conflict_flag


def generate_diff(
    timew_intervals: List[Interval], snapshot_intervals: List[Interval]
) -> Tuple[List[Interval], List[Interval]]:
    """Return the difference of intervals to the latest sync.

    Args:
        timew_intervals: A list of all client Interval objects.
        snapshot_intervals: A list of all Interval objects found in the snapshot of the latest sync.

    Returns:
        A Tuple of added and removed Interval objects.
    """
    added = [i for i in timew_intervals if i not in snapshot_intervals]
    removed = [i for i in snapshot_intervals if i not in timew_intervals]

    return added, removed
