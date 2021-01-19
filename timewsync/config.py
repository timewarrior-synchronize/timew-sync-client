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


import configparser


class Configuration:
    def __init__(self, server_base_url: str, user_id: int, merge_conflict_hook: str):
        self.server_base_url: str = server_base_url
        self.user_id: int = user_id
        self.merge_conflict_hook: str = merge_conflict_hook

    @classmethod
    def read(cls, path: str):
        config = configparser.ConfigParser()
        config.read(path)

        if "Server" in config:
            if "BaseURL" in config["Server"]:
                server_base_url = config.get("Server", "BaseURL")
            else:
                raise RuntimeError(
                    "The configuration file needs to define Server.BaseURL"
                )
        else:
            raise RuntimeError(
                'The configuration file needs to have a "Server" section'
            )

        if "Client" in config:
            if "UserID" in config["Client"]:
                user_id = config.getint("Client", "UserID")
            else:
                raise RuntimeError(
                    "The configuration file needs to define Client.UserID"
                )
            merge_conflict_hook = config.get(
                "Client", "OnMergeConflictHook", fallback=""
            )
        else:
            raise RuntimeError(
                'The configuration file needs to have a "Client" section'
            )

        return cls(server_base_url, user_id, merge_conflict_hook)
