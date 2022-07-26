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

from ansilog import bg


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

    def __call__(self, n):
        return self.get(n)

    def print_sample(self, index, name):
        color = self.base16colors[index]
        print('[', bg.rgb(color)(' ' * 10), ']', '0%X' % index, name)

    def print_all_samples(self):
        self.print_sample(0x00, "Default Background")
        self.print_sample(0x01, "Lighter Background (Used for status bars)")
        self.print_sample(0x02, "Selection Background")
        self.print_sample(0x03, "Comments, Invisibles, Line Highlighting")
        self.print_sample(0x04, "Dark Foreground (Used for status bars)")
        self.print_sample(0x05, "Default Foreground, Caret, Delimiters, Operators")
        self.print_sample(0x06, "Light Foreground (Not often used)")
        self.print_sample(0x07, "Light Background (Not often used)")
        self.print_sample(0x08, "Variables, XML Tags, Markup Link Text, Markup Lists, Diff Deleted")
        self.print_sample(0x09, "Integers, Boolean, Constants, XML Attributes, Markup Link Url")
        self.print_sample(0x0A, "Classes, Markup Bold, Search Text Background")
        self.print_sample(0x0B, "Strings, Inherited Class, Markup Code, Diff Inserted")
        self.print_sample(0x0C, "Support, Regular Expressions, Escape Characters, Markup Quotes")
        self.print_sample(0x0D, "Functions, Methods, Attribute IDs, Headings")
        self.print_sample(0x0E, "Keywords, Storage, Selector, Markup Italic, Diff Changed")
        self.print_sample(0x0F, "Deprecated, Open/Closing Embedded Language Tags, e.g. `<?php ?>`")

# --------------------------------------------------------------------
if __name__ == '__main__':
    Base16.load_from_xdefaults().print_all_samples()
