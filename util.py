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
from libqtile import qtile, hook
from libqtile.log_utils import logger

# --------------------------------------------------------------------
class MediaContainer:
    size_ratio = 3.0
    pad_ratio_x = 0.05
    pad_ratio_y = 0.1
    visible = True
    window: Optional[Window] = None

    @classmethod
    def make_media(cls, qtile: Qtile):
        """
        Make the current window the "media" window.
        """
        assert qtile.current_window is not None

        if qtile.current_window is cls.window:
            cls.forget_media()

        else:
            if cls.window is not None:
                cls.forget_media()
            cls.window = qtile.current_window
            cls.position_media_window(qtile)
            focus_last_non_floating_window(qtile)

    @classmethod
    def forget_media(cls, unfloat=True):
        """
        Forget about the media window, and unfloat it.
        """
        if unfloat and cls.window is not None:
            cls.window.floating = False
        cls.window = None
        # Reset for the next media window.
        cls.visible = True

    @classmethod
    def media_front_toggle(cls, qtile: Qtile):
        """
        Toggle the media to the front or back.

        If the current group is a different group, instead move the media
        window to that group and show it.
        """

        assert cls.window is not None
        cls.visible = not cls.visible

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
        info = qtile.current_screen.cmd_info()

        if not cls.visible:
            cls.window.minimized = True
            return

        cls.window.minimized = False

        width = info["width"]
        height = info["height"]

        media_width = int(width / cls.size_ratio)
        media_height = int(height / cls.size_ratio)

        offset_x = qtile.current_screen.x + int(
            max(0, width - media_width - (media_width * cls.pad_ratio_x))
        )
        offset_y = qtile.current_screen.y + int(max(0, media_height * cls.pad_ratio_y))

        if cls.size_ratio == 1:
            offset_x = 0
            offset_y = 0

        cls.window.cmd_set_size_floating(media_width, media_height)
        cls.window.cmd_set_position_floating(offset_x, offset_y)
        cls.window.cmd_bring_to_front()


# --------------------------------------------------------------------
@hook.subscribe.client_new
def on_window_open(window: Window):
    assert isinstance(qtile, Qtile)
    if MediaContainer.window is not None:
        MediaContainer.position_media_window(qtile)


# --------------------------------------------------------------------
@hook.subscribe.client_killed
def on_window_close(window: Window):
    assert isinstance(qtile, Qtile)
    if MediaContainer.window is not None:
        if MediaContainer.window.has_focus:
            focus_last_non_floating_window(qtile)
        if window is MediaContainer.window:
            MediaContainer.forget_media(unfloat=False)


# --------------------------------------------------------------------
@hook.subscribe.setgroup
def on_group_changed():
    assert isinstance(qtile, Qtile)
    if MediaContainer.window is not None:
        MediaContainer.position_media_window(qtile)


# --------------------------------------------------------------------
def focus_last_non_floating_window(qtile: Qtile):
    if MediaContainer.window is not None:
        group = qtile.current_group
        last_window = next(
            reversed(
                [w for w in group.focus_history if w is not w.floating]
            ),
            None,
        )
        if last_window is not None:
            group.focus(last_window)
        else:
            group.focus(None)

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
    assert qtile.current_window is not None
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen is True:
            qtile.cmd_to_screen(i + 1)
