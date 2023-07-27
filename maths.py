# --------------------------------------------------------------------
# math.py
#
# Author: Lain Musgrove (lain.musgrove@gmail.com)
# Date: Thursday July 27, 2023
# --------------------------------------------------------------------

from datetime import timedelta


# --------------------------------------------------------------------
def secs(sec: float) -> timedelta:
    return timedelta(seconds=sec)


# --------------------------------------------------------------------
def clamp(min_val, max_val, val):
    return max(min_val, min(max_val, val))
