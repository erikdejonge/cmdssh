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
from k8svp import *

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
        out = remote_cmd("localhost", "mkdir ~/Desktop/foobar")
        print(out)
        out = remote_cmd("localhost", "ls ~/Desktop/foobar")
        print (out)

    def test_run_cmd(self):
        """
        test_run_cmd
        """
        date = run_cmd("date", pr=False, shell=False, streamoutput=True, returnoutput=True)
        self.assertEqual(date, time.time())

    def test_scp(self):
        """
        test_scp
        """
        scp("localhost", "put", "./README.md", "./Desktop")
        out = remote_cmd("localhost", "ls ~/Desktop")
        print(out)


def main():
    """
    main
    """

    scp("localhost", "rabshakeh", "put", "./README.md", "./Desktop")
    #unit_test_main(globals())


if __name__ == "__main__":
    main()
