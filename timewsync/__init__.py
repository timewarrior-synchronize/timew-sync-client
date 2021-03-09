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
import os
import subprocess
import sys

import colorama
from colorama import Fore

from timewsync import auth, cli
from timewsync.dispatch import dispatch
from timewsync.file_parser import as_interval_list, as_file_strings, extract_tags
from timewsync.io_handler import read_data, write_data
from timewsync.config import Configuration

DEFAULT_DATA_DIR = os.path.join("~", ".timewsync")


def make_parser():
    """Creates an instance of argparse.ArgumentParser which contains the
    command-line arguments and their types.

    Returns:
        The complete ArgumentParser object
    """

    parser = argparse.ArgumentParser(prog="timewsync", description="timewarrior synchronization client")

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s unreleased",
        help="Print version information",
    )
    parser.add_argument(
        "--data-dir",
        dest="data_dir",
        default=DEFAULT_DATA_DIR,
        help="The path to the data directory",
    )

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.add_parser("generate-key", help="Generates a new key pair.")

    return parser


def run_conflict_hook(data_dir: str):
    """Run 'conflicts-occurred' file if present.

    Expected in '.timewsync/hooks' directory.

    Args:
        data_dir: The timewsync data directory.

    Raises:
        CalledProcessError: Is raised if the hook exits with a non-zero exit code. Holds details about the process.
    """
    conflict_hook = os.path.join(data_dir, "hooks", "conflicts-occurred")

    if os.path.exists(conflict_hook):
        subprocess.run(conflict_hook, check=True)


def main():
    """This function is the main entry point to the timewarrior
    synchronization client."""
    colorama.init()

    args = make_parser().parse_args()
    data_dir = os.path.expanduser(args.data_dir)

    configuration = Configuration.read(data_dir, "timewsync.conf")

    if args.subcommand == "generate-key":
        generate_key(configuration)
        return

    sync(configuration)


def sync(configuration: Configuration) -> None:
    """Sync's the timewarrior data with the server.

    Args:
        configuration: The user's configuration.
    """
    timew_data, snapshot_data = read_data(configuration.data_dir)
    timew_intervals, active_interval = as_interval_list(timew_data)
    snapshot_intervals, _ = as_interval_list(snapshot_data)

    if active_interval:
        sys.stderr.write("Time tracking is active. Stopped time tracking.\n")

    private_key, _ = io_handler.read_keys(configuration.data_dir)
    token = auth.generate_jwt(private_key, configuration.user_id)

    response_intervals, conflict_flag = dispatch(
        configuration, timew_intervals, snapshot_intervals, token
    )

    if conflict_flag:
        run_conflict_hook(configuration.data_dir)

    server_data, started_tracking = as_file_strings(response_intervals, active_interval)
    new_tags = extract_tags(response_intervals)
    write_data(configuration.data_dir, server_data, new_tags)

    sys.stderr.write("Synced successfully!\n")

    if active_interval:
        if started_tracking:
            sys.stderr.write("Restarted time tracking.\n")
        else:
            sys.stderr.write(Fore.RED + "Warning: Cannot restart time tracking!\n" + Fore.RESET)


def generate_key(configuration: Configuration):
    """Generates a new RSA key pair.

    Prompts the user for confirmation if keys already exist.

    Args:
        configuration: The user's configuration.
    """
    priv_pem, pub_pem = io_handler.read_keys(configuration.data_dir)

    if priv_pem or pub_pem:
        confirm = cli.confirmation_reader(
            "The timewsync folder already contains keys. They will be overwritten. Do you want to continue?"
        )
        if not confirm:
            return

    priv_pem, pub_pem = auth.generate_keys()
    io_handler.write_keys(configuration.data_dir, priv_pem, pub_pem)

    sys.stderr.write(
        f"A new key pair was generated. You can find it in your timewsync folder ({configuration.data_dir})."
    )
