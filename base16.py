# --------------------------------------------------------------------
# base16.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Saturday May 9, 2020
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------

"""
A simple wrapper around Base16 colorschemes.
"""

import re
from pathlib import Path
from typing import List


# --------------------------------------------------------------------
class Base16:
    def __init__(self, base16colors: List[str]):
        self.base16colors = base16colors

    @classmethod
    def load_from_xdefaults(cls):
        xdefaults_file = Path.home() / ".Xdefaults"

        base16 = list([''] * 16)

        with open(xdefaults_file, "r") as infile:
            for line in infile.readlines():
                match = re.match(r"#define base(.*) #(.*)$", line.strip())
                if match:
                    base16[int(match.group(1), base=16)] = match.group(2)

        if any(v == '' for v in base16):
            raise ValueError('Failed to parse base16 colorscheme from ~/.Xdefaults.')

        return Base16(base16)

    def get(self, n):
        if n < 0 or n > 0x10:
            raise ValueError('Value must be between 0 and 15.')
        return self.base16colors[n]

    @property
    def background(self):
        return self.get(0x00)

    @property
    def lighter_background(self):
        return self.get(0x01)

    @property
    def selection_background(self):
        return self.get(0x02)

    @property
    def comment(self):
        return self.get(0x03)

    @property
    def dark_foreground(self):
        return self.get(0x04)

    @property
    def foreground(self):
        return self.get(0x05)

    @property
    def light_foreground(self):
        return self.get(0x06)

    @property
    def light_background(self):
        return self.get(0x07)

    @property
    def variable(self):
        return self.get(0x08)

    @property
    def constant(self):
        return self.get(0x09)

    @property
    def type(self):
        return self.get(0x0A)

    @property
    def string(self):
        return self.get(0x0B)

    @property
    def escape(self):
        return self.get(0x0C)

    @property
    def function(self):
        return self.get(0x0D)

    @property
    def keyword(self):
        return self.get(0x0E)

    @property
    def deprecated(self):
        return self.get(0x0F)
