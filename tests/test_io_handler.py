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


import unittest
from timewsync import io_handler


class TestExtractFileName(unittest.TestCase):
    def test_1_no_entry(self):
        self.assertRaises(AssertionError, io_handler.extract_file_name, '')

    def test_2_short_entry(self):
        self.assertEqual(io_handler.extract_file_name('inc 20200931T235500Z'), '2020-09.data')

    def test_3_long_entry(self):
        self.assertEqual(io_handler.extract_file_name('inc 20200931T235500Z - 20201001T000500Z'), '2020-10.data')

    def test_4_multiple_entries(self):
        self.assertEqual(io_handler.extract_file_name(
            """inc 20201208T133105Z - 20201208T133134Z # 10
            inc 20201208T134704Z - 20201208T134712Z
            inc 20201208T135322Z # 10
            different dates are not expected here"""
        ), '2020-12.data')
