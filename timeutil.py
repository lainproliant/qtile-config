# --------------------------------------------------------------------
# timeutil.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Friday September 15, 2023
# --------------------------------------------------------------------

import time

# --------------------------------------------------------------------
def get_millis() -> int:
    return int(round(time.time() * 1000))
