# --------------------------------------------------------------------
# widget.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Saturday May 9, 2020
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------

"""
Contains simple custom widgets used in the status bar.
"""

from typing import List

import iwlib
import netifaces
import psutil
from libqtile.log_utils import logger
from libqtile.widget.base import ORIENTATION_HORIZONTAL, InLoopPollText
from libqtile.widget.memory import Memory


# --------------------------------------------------------------------
# pylint: disable=R0901
# (too many ancestors)
class CustomMemory(Memory):
    defaults = [
        ("format", "#{MemPercent:02.0f}% ", "Formatting for field names."),
        ("update_interval", 1.0, "Update interval for the Memory"),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(CustomMemory.defaults)

    def poll(self):
        mem = psutil.virtual_memory()
        val = {}
        val["MemPercent"] = (mem.used / mem.total) * 100
        return self.format.format(**val)


# --------------------------------------------------------------------
class CustomNetwork(InLoopPollText):
    """
    Displays active wifi and ethernet connections.  Wifi connections
    are paired with essid and connection quality.

    Uses iwlib and netifaces.
    """

    orientations = ORIENTATION_HORIZONTAL
    defaults = [
        ("update_interval", 1, "The update interval."),
        ("eth_format", "{iface}:{addresses}", "The format for ethernet ifaces."),
        (
            "wifi_format",
            "{iface}:{addresses}/{essid}",
            "The format for wifi ifaces",
        ),
    ]

    def __init__(self, **config):
        InLoopPollText.__init__(self, **config)
        self.add_defaults(CustomNetwork.defaults)

    @classmethod
    def get_addresses(cls, iface: str) -> List[str]:
        # pylint: disable=I1101
        ifaddrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in ifaddrs:
            return [addr["addr"] for addr in ifaddrs[netifaces.AF_INET]]
        return []

    def format_wifi(self, statuses: List[str], iface: str):
        interface = iwlib.get_iwconfig(iface)
        if "stats" not in interface:
            return
        quality = interface["stats"]["quality"]
        essid = bytes(interface["ESSID"]).decode()
        addresses = self.get_addresses(iface)
        if addresses:
            statuses.append(
                self.wifi_format.format(
                    essid=essid,
                    iface=iface,
                    addresses=",".join(addresses),
                )
            )

    def format_eth(self, statuses: List[str], iface: str):
        addresses = self.get_addresses(iface)
        if addresses:
            statuses.append(
                self.eth_format.format(
                    iface=iface,
                    addresses=",".join(addresses),
                )
            )

    def poll(self):
        statuses: List[str] = []
        try:
            # pylint: disable=I1101
            ifaces = netifaces.interfaces()
            wifi_ifaces = [iface for iface in ifaces if iface.startswith("wl")]
            eth_ifaces = [iface for iface in ifaces if iface.startswith("en")]

            for iface in wifi_ifaces:
                self.format_wifi(statuses, iface)

            for iface in eth_ifaces:
                self.format_eth(statuses, iface)

            return " ".join(statuses)

        except Exception:
            logger.exception("CustomNetwork is broke!")
