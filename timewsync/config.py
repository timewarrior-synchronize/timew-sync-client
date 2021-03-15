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


import configparser
import os

CONFIGURATION_FILE_NAME = "timewsync.conf"
EXAMPLE_CONFIGURATION = """
# This is an example of the configuration file format for the
# timewarrior synchronization client

# Copy this file to $TIMEWSYNC/timewsync.conf where $TIMEWSYNC is your
# timewarrior synchronization data directory. This defaults to
# ~/.timewsync

[Server]
# The base URL of the server. Required
#BaseURL = http://timew.sync.domain:8080

[Client]
# User id. Required
#UserID = 1234
"""


class NoConfigurationFileError(Exception):
    """A configuration file was not found"""

    pass


class MissingSectionError(Exception):
    """A section is missing from the configuration file

    Attributes:
        section: The section which is missing
    """

    def __init__(self, section: str):
        self.section: str = section


class MissingConfigurationError(Exception):
    """A section is missing from the configuration file

    Attributes:
        section: The section in which the missing configuration is supposed to be
        name: The name of the configuration parameter
    """

    def __init__(self, section: str, name: str):
        self.section: str = section
        self.name: str = name


class Configuration:
    """Holds all configuration options defined in the timewsync client
    configuration file

    Attributes:
        data_dir: The path to the timewsync data directory
        server_base_url: The base URL (API Endpoint) of the synchronization server
        user_id: The unique ID of the timewsync user
    """

    def __init__(self, data_dir: str, server_base_url: str, user_id: int):
        self.data_dir = data_dir
        self.server_base_url: str = server_base_url
        self.user_id: int = user_id

    @classmethod
    def read(cls, data_dir: str):
        """Reads the configuration from the configuration file in the
        timewsync data directory.

        Args:
            data_dir: The path to the timewsync data directory

        Raises:
            NoConfigurationFileError: The configuration file does not exist
            MissingSectionError: A mandatory section is missing from the configuration file
            MissingConfigurationError: A mandatory variable is missing from the configuration file
        """
        path = os.path.join(data_dir, CONFIGURATION_FILE_NAME)
        if not os.path.isfile(path):
            raise NoConfigurationFileError()

        config = configparser.ConfigParser()
        config.read(path)

        if "Server" in config:
            if "BaseURL" in config["Server"]:
                server_base_url = config.get("Server", "BaseURL")
            else:
                raise MissingConfigurationError("Server", "BaseURL")
        else:
            raise MissingSectionError("Server")

        if "Client" in config:
            if "UserID" in config["Client"]:
                user_id = config.getint("Client", "UserID")
            else:
                raise MissingConfigurationError("Client", "UserID")
        else:
            raise MissingSectionError("Client")

        return cls(data_dir, server_base_url, user_id)


def create_example_configuration(data_dir: str) -> str:
    """Writes an example configuration to the data directory

    Args:
        data_dir: The path to the timewsync data directory

    Returns:
        The path to the configuration file
    """
    path = os.path.join(data_dir, CONFIGURATION_FILE_NAME)

    with open(path, "w") as file:
        file.write(EXAMPLE_CONFIGURATION)

    return path
