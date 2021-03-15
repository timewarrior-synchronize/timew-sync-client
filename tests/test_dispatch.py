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


from timewsync.dispatch import generate_diff
from timewsync.interval import Interval


class TestGenerateDiff:
    def test_empty_list(self):
        """Test with both lists having no data."""
        assert generate_diff([], []) == ([], [])

    def test_added_list(self):
        """Test with only the 'added' list having data."""
        assert generate_diff([Interval()], []) == ([Interval()], [])
        assert generate_diff([Interval(tags=["foo"]), Interval(tags=["bar"])], [Interval(tags=["foo"])]) == (
            [Interval(tags=["bar"])],
            [],
        )

    def test_removed_list(self):
        """Test with only the 'removed' list having data."""
        assert generate_diff([], [Interval()]) == ([], [Interval()])
        assert generate_diff([Interval(tags=["foo"])], [Interval(tags=["foo"]), Interval(tags=["bar"])]) == (
            [],
            [Interval(tags=["bar"])],
        )

    def test_both_lists(self):
        """Test with both lists having data."""
        unchanged_interval = Interval(tags=["foo"], annotation="this is unchanged")
        added_interval = Interval(tags=["bar"], annotation="this has been added")
        removed_interval = Interval(tags=["bar"], annotation="this has been removed")
        assert generate_diff([unchanged_interval], [unchanged_interval]) == ([], [])
        assert generate_diff([unchanged_interval, added_interval], [removed_interval, unchanged_interval]) == (
            [added_interval],
            [removed_interval],
        )
