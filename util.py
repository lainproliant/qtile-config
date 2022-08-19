# --------------------------------------------------------------------
# util.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Tuesday August 16, 2022
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------

from typing import Optional

from libqtile.core.manager import Qtile
from libqtile.backend.base import Window

# --------------------------------------------------------------------
class MediaContainer:
    window: Optional[Window] = None

# --------------------------------------------------------------------
def toggle_focus_floating(qtile: Qtile):
    assert qtile.current_window is not None
    group = qtile.current_group

    for win in reversed(group.focus_history):
        if qtile.current_window.floating and not win.floating:
            group.focus(win)
            break

        if not qtile.current_window.floating and win.floating:
            group.focus(win)
            break


# --------------------------------------------------------------------
def make_media(qtile: Qtile):
    """
    Make the current window the "media" window.
    """
    assert qtile.current_window is not None

    info = qtile.current_screen.cmd_info()
    width = info["width"]
    height = info["height"]
    media_width = width / 3
    media_height = height / 3
    qtile.current_window.cmd_set_size_floating(media_width, media_height)
    qtile.current_window.cmd_set_position(
        width - media_width - (media_width / 8), media_height / 5
    )
    MediaContainer.window = qtile.current_window


# --------------------------------------------------------------------
def floats_to_front(qtile: Qtile):
    """
    Bring all floating windows of the group to front
    """
    for window in qtile.current_group.windows:
        if window.floating:
            window.cmd_bring_to_front()


# --------------------------------------------------------------------
def media_to_front(qtile: Qtile):
    """
    Bring the media window to front.
    """

    assert MediaContainer.window is not None
    prev_window = qtile.current_window
    MediaContainer.window.togroup(qtile.current_group.name, switch_group=True)
    MediaContainer.window.cmd_bring_to_front()

    if prev_window is not None:
        prev_window.cmd_focus()


# --------------------------------------------------------------------
def window_to_prev_screen(qtile: Qtile, switch_group=False, switch_screen=False):
    assert qtile.current_window is not None
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen is True:
            qtile.cmd_to_screen(i - 1)


# --------------------------------------------------------------------
def window_to_next_screen(qtile: Qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen is True:
            qtile.cmd_to_screen(i + 1)
