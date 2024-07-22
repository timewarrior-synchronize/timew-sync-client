###############################################################################
#
# Copyright 2020 - 2024, Jan Bormet, Anna-Felicitas Hausmann, Joachim Schmidt, Vincent Stollenwerk, Arne Turuc
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


"""Provides file locations of timewarrior data and configuration.

This module follows the same priority order timewarrior uses to provide the correct data and config locations.
The final locations may be accessed using `paths.CONFIG_FILE`, `paths.DB_DATA_DIR` and `paths.EXTENSIONS_DIR`fields.

The priority order is as follows:
1. `TIMEWARRIORDB` environment variable
2. If already existing or not unix-like OS: `.timewarrior` in user directory
3. `XDG_DATA_HOME` and `XDG_CONFIG_HOME` environment variables, in `timewarrior` subdirectory
4. `.local/share/timewarrior` and `.config/timewarrior`

Reference file from timewarrior:
https://github.com/GothenburgBitFactory/timewarrior/blob/develop/src/paths.cpp
"""


import os
import sys

_timewarriordb = os.getenv("TIMEWARRIORDB")
_legacy_config_dir = "~/.timewarrior"

_uses_legacy_config = os.path.isdir(os.path.expanduser(_legacy_config_dir))
_unix_like = any(sys.platform.startswith(os_name) for os_name in {"darwin", "linux", "freebsd"})

# Set config and database locations
if _timewarriordb:
    _config_dir = _db_dir = _timewarriordb
elif _uses_legacy_config or not _unix_like:
    _config_dir = _db_dir = _legacy_config_dir
else:
    _config_dir = os.getenv("XDG_CONFIG_HOME", "~/.config") + "/timewarrior"
    _db_dir = os.getenv("XDG_DATA_HOME", "~/.local/share") + "/timewarrior"

# Final paths
CONFIG_FILE = os.path.expanduser(_config_dir + "/timewarrior.cfg")
DB_DATA_DIR = os.path.expanduser(_db_dir + "/data")
EXTENSIONS_DIR = os.path.expanduser(_config_dir + "/extensions")
