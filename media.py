# --------------------------------------------------------------------
# media.py
#
# Author: Lain Musgrove (lain.musgrove@gmail.com)
# Date: Wednesday July 26, 2023
# --------------------------------------------------------------------

from typing import Optional

from libqtile import hook, qtile
from libqtile.backend.base import Window
from libqtile.core.manager import Qtile

from constants import Subjects
from maths import clamp
from status import Status


# --------------------------------------------------------------------
class MediaContainer:
    MIN_SIZE = 0.1
    MAX_SIZE = 0.5
    MIN_PAD = 0.0
    MAX_PAD = 1.0

    size = 0.2
    pad_x = 0.0
    pad_y = 0.02
    aspect_x = 1.6
    aspect_y = 0.9
    visible = True

    window: Optional[Window] = None

    @classmethod
    def toggle_media(cls, qtile: Qtile):
        """
        Make the current window the "media" window, or forget the media window.
        """
        assert qtile.current_window is not None

        if cls.window is not None:
            cls.forget_media()

        else:
            cls.set_media(qtile, qtile.current_window)

    @classmethod
    def set_media(cls, qtile: Qtile, window):
        cls.forget_media(focus=False)
        cls.window = window
        cls.position_media_window(qtile, True)

    @classmethod
    def forget_media(cls, unfloat=True, focus=True):
        """
        Forget about the media window, and unfloat it.
        """
        if cls.window is not None:
            cls.focus_last_non_floating_window(qtile)
            if unfloat:
                cls.window.floating = False
            if focus:
                cls.window.focus(True)

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
    def adjust_size(cls, ratio: float):
        def _adjust_size(qtile: Qtile):
            cls.size = clamp(cls.MIN_SIZE, cls.MAX_SIZE, cls.size + ratio)
            cls.position_media_window(qtile, True)

        return _adjust_size

    @classmethod
    def adjust_pad_x(cls, ratio: float):
        def _adjust_pad_x(qtile: Qtile):
            cls.pad_x = max(0, cls.pad_x + ratio)
            cls.position_media_window(qtile, True)

        return _adjust_pad_x

    @classmethod
    def adjust_pad_y(cls, ratio: float):
        def _adjust_pad_y(qtile: Qtile):
            cls.pad_y = max(0, cls.pad_y + ratio)
            cls.position_media_window(qtile, True)

        return _adjust_pad_y

    @classmethod
    def adjust_opacity(cls, delta: float):
        def _adjust_opacity(qtile: Qtile):
            assert cls.window is not None
            cls.window.opacity = clamp(0.1, 1.0, cls.window.opacity + delta)

        return _adjust_opacity

    @classmethod
    def position_media_window(cls, qtile: Qtile, print_status=False):
        assert cls.window is not None
        info = qtile.current_screen.cmd_info()

        if not cls.visible:
            cls.window.minimized = True
            return

        cls.window.minimized = False

        width = info["width"]
        height = info["height"]

        media_height = int(height * cls.size)
        media_width = int(media_height * (cls.aspect_x / cls.aspect_y))

        offset_x = qtile.current_screen.x + int(
            max(0, width - media_width - (width * cls.pad_x))
        )
        offset_y = qtile.current_screen.y + int(max(0, height * cls.pad_y))

        cls.window.cmd_set_size_floating(media_width, media_height)
        cls.window.cmd_set_position_floating(offset_x, offset_y)
        cls.window.cmd_bring_to_front()

        if print_status:
            Status.show(Subjects.WINDOW_SIZE, f"{media_width}x{media_height}")

    @classmethod
    def focus_last_non_floating_window(cls, qtile: Qtile):
        if cls.window is not None:
            group = qtile.current_group
            windows = reversed([w for w in group.focus_history if not w.floating])
            last_window = next(windows, None)

        if last_window is MediaContainer.window:
            last_window = next(windows, None)

        if last_window is not None:
            group.focus(last_window)
        else:
            group.focus(None)

    @classmethod
    def setup_hooks(cls):
        @hook.subscribe.client_new
        def on_window_open(window: Window):
            assert isinstance(qtile, Qtile)
            if MediaContainer.window is not None:
                MediaContainer.position_media_window(qtile)

        @hook.subscribe.client_killed
        def on_window_close(window: Window):
            assert isinstance(qtile, Qtile)
            if MediaContainer.window is not None:
                cls.focus_last_non_floating_window(qtile)
                if window is MediaContainer.window:
                    MediaContainer.forget_media(unfloat=False)

        @hook.subscribe.setgroup
        def on_group_changed():
            assert isinstance(qtile, Qtile)
            if MediaContainer.window is not None:
                MediaContainer.position_media_window(qtile)

        @hook.subscribe.client_focus
        def no_focus_mediawindow(window):
            if window == MediaContainer.window:
                cls.focus_last_non_floating_window(qtile)
