# Client reads tw data
import os
import re
from pathlib import Path


def read_data():
    """Return a list of strings each of which containing all lines from a single monthly file in .timewarrior/data."""
    # Navigate to .home/.timewarrior/data
    data_folder = Path(os.path.expanduser('~') + "/.timewarrior/data")
    # Make a list from all .data files you shall read
    file_list = [f for f in os.listdir(data_folder) if (re.search('\d\d\d\d-\d\d.data', f))]
    # Iterate over the list and read each file (= month). Write the content of each file into a list of strings: one string for each file.
    return [(open(os.path.expanduser('~') + "/.timewarrior/data/" + file).read()) for file in file_list]
