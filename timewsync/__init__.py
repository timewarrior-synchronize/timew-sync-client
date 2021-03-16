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


import argparse
import logging
import os
import subprocess
import sys

import colorama
from colorama import Fore
import requests

from timewsync import auth, cli
from timewsync.dispatch import ServerError, dispatch
from timewsync.file_parser import as_interval_list, as_file_strings, extract_tags
from timewsync.io_handler import read_data, read_keys, write_data, write_keys, delete_snapshot
from timewsync.config import NoConfigurationFileError, MissingSectionError, MissingConfigurationError, Configuration
from timewsync.logging_helpers import MinMaxLevelFilter

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
        help="print version information",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug output",
    )
    parser.add_argument(
        "--data-dir",
        dest="data_dir",
        default=DEFAULT_DATA_DIR,
        help="the path to the data directory",
    )

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.add_parser("generate-key", help="generates a new key pair.")

    return parser


def run_conflict_hook(data_dir: str) -> None:
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

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    red_formatter = logging.Formatter(Fore.RED + "%(levelname)s: %(message)s" + Fore.RESET)
    red_handler = logging.StreamHandler(sys.stderr)
    red_handler.addFilter(MinMaxLevelFilter(logging.WARNING, logging.CRITICAL))
    red_handler.setFormatter(red_formatter)
    log.addHandler(red_handler)

    if args.verbose:
        debug_formatter = logging.Formatter("%(levelname)s: %(message)s")
        debug_handler = logging.StreamHandler(sys.stderr)
        debug_handler.addFilter(MinMaxLevelFilter(logging.DEBUG, logging.INFO))
        debug_handler.setFormatter(debug_formatter)
        log.addHandler(debug_handler)

    try:
        configuration = Configuration.read(data_dir)
    except NoConfigurationFileError:
        config_file_path = config.create_example_configuration(data_dir)
        log.error(
            'No configuration file could not be found. An example configuration file was written to "%s". '
            "This file is still incomplete. An edit to match the server setup is necessary.",
            config_file_path,
        )
        return
    except MissingSectionError as e:
        log.error('The configuration file needs to define the section "%s".', e.section)
        return
    except MissingConfigurationError as e:
        log.error('The section "%s" in the configuration needs to define "%s".', e.section, e.name)
        return

    if args.subcommand == "generate-key":
        generate_key(configuration)
        return

    sync(configuration)


def sync(configuration: Configuration) -> None:
    """Sync's the timewarrior data with the server.

    Args:
        configuration: The user's configuration.
    """
    log = logging.getLogger(__name__)

    # Read data
    try:
        timew_data, snapshot_data = read_data(configuration.data_dir)
        timew_intervals, active_interval = as_interval_list(timew_data)
        snapshot_intervals, _ = as_interval_list(snapshot_data)
    except OSError as e:
        log.debug("OSError: %s", e)
        log.error("Error reading intervals from disk: No changes were made.")
        return

    # Read key
    try:
        private_key, _ = read_keys(configuration.data_dir)
        if private_key is None:
            log.error("No private key was found. Generate a key pair using `timewsync generate-key`.")
            return
    except OSError as e:
        log.debug("OSError: %s", e)
        log.error("Error reading private key from disk: No changes were made.")
        return

    # Generate token
    try:
        token = auth.generate_jwt(private_key, configuration.user_id)
    except Exception as e:
        log.debug("Unexpected Exception: %s", e)
        log.error("Unexpected error occurred during JWT generation. No changes were made.")
        return

    # Communicate with server
    try:
        response_intervals, conflict_flag = dispatch(configuration, timew_intervals, snapshot_intervals, token)
    except requests.ConnectionError as e:
        log.debug("Connection error: %s", e)
        log.error("Error connecting to server. No changes were made.")
        return
    except ServerError as e:
        log.debug("Error details: %s", e.details)
        log.error('Server responded with error message "%s". No changes were made.', e.message)
        return
    except Exception as e:
        log.debug("Unexpected Exception: %s", e)
        log.error("Unexpected error occurred during communication with server. No changes were made.")
        return

    # Write data
    try:
        server_data, started_tracking = as_file_strings(response_intervals, active_interval)
        new_tags = extract_tags(response_intervals)
        write_data(configuration.data_dir, server_data, new_tags)
    except IOError as e:
        delete_snapshot(configuration.data_dir)
        log.debug("IOError: %s", e)
        log.error("Error writing data to disk. To ensure consistency, the newly created snapshot was deleted.")
        return
    except Exception as e:
        delete_snapshot(configuration.data_dir)
        log.debug("Unexpected Exception: %s", e)
        log.error(
            "Unexpected error occurred during writing of data. "
            "To ensure consistency, the newly created snapshot was deleted."
        )
        return

    # Run hook if necessary
    if conflict_flag:
        try:
            run_conflict_hook(configuration.data_dir)
        except subprocess.CalledProcessError:
            log.warning("Hook exited with a non-zero exit code. Continuing...")
        except OSError as e:
            log.debug("OSError: %s", e)
            log.error("Error occurred while executing the conflict-occurred hook. Continuing...")

    # Output
    if active_interval:
        print("Time tracking is active. Stopped time tracking.", file=sys.stderr)

    print("Synchronization successful!", file=sys.stderr)

    if active_interval:
        if started_tracking:
            print("Restarted time tracking.", file=sys.stderr)
        else:
            log.warning(
                "Warning: Cannot restart time tracking! This error occured because there exists "
                "an interval in the future which would overlap with the open interval."
            )


def generate_key(configuration: Configuration) -> None:
    """Generates a new RSA key pair.

    Prompts the user for confirmation if keys already exist.

    Args:
        configuration: The user's configuration.
    """
    log = logging.getLogger(__name__)

    priv_pem, pub_pem = read_keys(configuration.data_dir)

    if priv_pem or pub_pem:
        confirm = cli.confirmation_reader(
            "The timewsync folder already contains keys. They will be overwritten. Do you want to continue?"
        )
        if not confirm:
            return

    try:
        priv_pem, pub_pem = auth.generate_keys()
    except Exception as e:
        log.error("Unexpected error occurred while generating keys: %s", e)
        return

    try:
        write_keys(configuration.data_dir, priv_pem, pub_pem)
    except OSError as e:
        log.error("Error occurred while writing new keys: %s", e)
        return

    print(
        f"A new key pair was generated. You can find it in your timewsync folder ({configuration.data_dir}).",
        file=sys.stderr,
    )
