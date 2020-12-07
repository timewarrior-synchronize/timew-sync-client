# Client reads tw data
import os
import re
import pathlib
from pathlib import Path

def read_data():
    """Gets nothing and returns a list of strings which are the lines from all month-.files from .timewarrior/data"""
    # Navigate to .home/.timewarrior/data
    data_folder = Path(os.path.expanduser('~') + "/.timewarrior/data")
    # Make a list from all .data-files you shall read
    file_list = [f for f in os.listdir(data_folder) if (re.search('\d\d\d\d-\d\d.data', f)) ]
    # Iterate over the list and read each file(= month). Write the content of each file into a list of strings: one string for each file.
    return [(open("/home/afh/.timewarrior/data/" + file).read()) for file in file_list]
