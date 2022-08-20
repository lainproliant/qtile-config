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
    size_ratio = 3.0
    pad_ratio_x = 0.05
    pad_ratio_y = 0.1

    window: Optional[Window] = None

    @classmethod
    def make_media(cls, qtile: Qtile):
        """
        Make the current window the "media" window.
        """
        assert qtile.current_window is not None
        prev_window = qtile.current_window

        cls.window = qtile.current_window
        cls.position_media_window(qtile)

        if prev_window is not None:
            prev_window.cmd_focus()

    @classmethod
    def media_to_front(cls, qtile: Qtile):
        """
        Bring the media window to front.
        """

        assert cls.window is not None
        cls.position_media_window(qtile)

    @classmethod
    def adjust_size_ratio(cls, ratio: float):
        def _adjust_size_ratio(qtile: Qtile):
            cls.size_ratio = max(1.0, cls.size_ratio + ratio)
            cls.position_media_window(qtile)

        return _adjust_size_ratio

    @classmethod
    def adjust_pad_ratio_x(cls, ratio: float):
        def _adjust_pad_ratio_x(qtile: Qtile):
            cls.pad_ratio_x = max(0, cls.pad_ratio_x + ratio)
            cls.position_media_window(qtile)

        return _adjust_pad_ratio_x

    @classmethod
    def adjust_pad_ratio_y(cls, ratio: float):
        def _adjust_pad_ratio_y(qtile: Qtile):
            cls.pad_ratio_y = max(0, cls.pad_ratio_y + ratio)
            cls.position_media_window(qtile)

        return _adjust_pad_ratio_y

    @classmethod
    def position_media_window(cls, qtile: Qtile):
        assert cls.window is not None
        prev_window = qtile.current_window
        info = qtile.current_screen.cmd_info()

        width = info["width"]
        height = info["height"]
        media_width = width / cls.size_ratio
        media_height = height / cls.size_ratio

        offset_x = max(0, width - media_width - (media_width * cls.pad_ratio_x))
        offset_y = max(0, media_height * cls.pad_ratio_y)

        if cls.size_ratio == 1:
            offset_x = 0
            offset_y = 0

        cls.window.cmd_set_size_floating(media_width, media_height)
        cls.window.cmd_set_position(offset_x, offset_y)

        cls.window.togroup(qtile.current_group.name, switch_group=True)
        cls.window.cmd_bring_to_front()

        if prev_window is not None:
            prev_window.cmd_focus()


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
def adjust_opacity(delta: float):
    def _adjust_opacity(qtile: Qtile):
        assert qtile.current_window is not None
        opacity = qtile.current_window.opacity + delta
        opacity = max(0.1, min(1.0, opacity))
        qtile.current_window.opacity = opacity

    return _adjust_opacity


# --------------------------------------------------------------------
def floats_to_front(qtile: Qtile):
    """
    Bring all floating windows of the group to front
    """
    for window in qtile.current_group.windows:
        if window.floating:
            window.cmd_bring_to_front()


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
