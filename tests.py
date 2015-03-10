# coding=utf-8
# coding=utf-8
"""
unittester
-
Active8 (05-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from unittester import *
from cmdssh import *

import time


class CmdsshTestCase(unittest.TestCase):
    """
    @type unittest.TestCase: str, unicode
    @return: None
    """
    def test_command(self):
        """
        test_assert_raises
        """
        remote_cmd("localhost", "rm -Rf ~/Desktop/foobar")
        remote_cmd("localhost", "mkdir ~/Desktop/foobar")
        out = remote_cmd("localhost", "ls ~/Desktop")
        x = "foobar" in out
        self.assertTrue(x)

        remote_cmd("localhost", "rmdir ~/Desktop/foobar")
        out = remote_cmd("localhost", "ls ~/Desktop")
        x = "foobar.md" in out
        self.assertFalse(x)

    def test_run_cmd(self):
        """
        test_run_cmd
        """
        localt = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        date = run_cmd('date "+%Y-%m-%d% %H:%M"', pr=False, streamoutput=False, returnoutput=True)
        self.assertEqual(date, localt)

    def test_scp(self):
        """
        test_scp
        """
        run_scp("localhost", "rabshakeh", "put", "./README.md", "./Desktop")
        out = remote_cmd("localhost", "ls ~/Desktop")
        x = "README.md" in out
        self.assertTrue(x)


def main():
    """
    main
    """
    unit_test_main(globals())


if __name__ == "__main__":
    main()
