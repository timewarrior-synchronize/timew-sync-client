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


import argparse
import configparser
import os

from timewsync.dispatch import dispatch
from timewsync.file_parser import to_interval_list, to_monthly_data
from timewsync.io_handler import read_data, write_data


def make_parser():
    """Creates an instance of argpars.ArgumentParser which contains the
    command-line arguments and their types.

    Returns:
        The complete ArgumentParser object
    """

    parser = argparse.ArgumentParser(prog="timewsync", description="timewarrior synchronization client")

    parser.add_argument("--version", action="version", version="%(prog)s unreleased", help="Print version information")
    parser.add_argument("--config-file", dest="config_file", default="~/.timewarrior/sync.conf", help="The path to the configuration file")

    return parser


def main():
    """This function is the main entry point to the timewarrior
    synchronization client."""
    args = make_parser().parse_args()

    config = configparser.ConfigParser()
    config.read(os.path.expanduser(args.config_file))
    base_url = config.get("Server", "BaseURL", fallback="http://localhost:8080")

    client_data = read_data()
    request_intervals = to_interval_list(client_data)
    # TODO store unrecorded interval after api design update (assignee: Arne)
    # TODO filter corrupted intervals after api design update (assignee: Arne)
    response_intervals = dispatch(base_url, request_intervals)
    server_data = to_monthly_data(response_intervals)
    # TODO load unrecorded interval after api design update (assignee: Arne)
    write_data(server_data)
