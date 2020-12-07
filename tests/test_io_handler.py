import os
import re
import pathlib
from pathlib import Path
import timewsync.io_handler

def test_read_data():
    # write a testfile
    testfile = open((os.path.expanduser('~') + "/.timewarrior/data/0000-00.data"), 'w')
    testfile.write("This is a test.\nAnd this is its second line.")
    testfile.close()

    assert ("This is a test.\nAnd this is its second line." in timewsync.io_handler.read_data())

    os.remove(os.path.expanduser('~') + "/.timewarrior/data/0000-00.data")

test_read_data()
