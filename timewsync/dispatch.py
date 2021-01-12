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
from typing import List, Tuple

import requests

from timewsync import json_converter
from timewsync.interval import Interval

SYNC_ENDPOINT = os.path.join('api', 'sync')


def dispatch(base_url: str, timew_intervals: List[Interval], snapshot_intervals: List[Interval]) -> List[Interval]:
    """Sends a sync request to the server.

    Args:
        base_url: The base URL of the API. E.g.: "http://localhost:8080".
        timew_intervals: A list of all client Interval objects.
        snapshot_intervals: A list of all Interval objects found in snapshot.

    Returns:
        A list of Interval objects resulting from the sync.
    """
    request_url = os.path.join(base_url, SYNC_ENDPOINT)
    request_body = json_converter.to_json_request(timew_intervals)

    server_response = requests.put(request_url, request_body)

    if server_response.status_code != 200:
        raise RuntimeError(f'Problem while syncing with server. Server responded with {server_response.status_code}.')

    parsed_response = json_converter.to_interval_list(server_response.text)

    return parsed_response


def generate_diff(timew_intervals: List[Interval], snapshot_intervals: List[Interval]) -> Tuple[List[Interval], List[Interval]]:
    """Returns the difference of intervals to the latest sync.

     Args:
         timew_intervals: A list of all client Interval objects.
         snapshot_intervals: A list of all Interval objects found in snapshot.

     Returns:
         A Tuple of added and removed Interval objects.
     """
    added = [i for i in timew_intervals if i not in snapshot_intervals]
    removed = [i for i in snapshot_intervals if i not in timew_intervals]

    return added, removed
