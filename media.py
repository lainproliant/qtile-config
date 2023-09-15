# --------------------------------------------------------------------
# media.py
#
# Author: Lain Musgrove (lain.musgrove@gmail.com)
# Date: Wednesday July 26, 2023
# --------------------------------------------------------------------

from typing import Optional

from dataclasses import dataclass
from libqtile import hook, qtile
from libqtile.backend.base import Window
from libqtile.core.manager import Qtile

from timeutil import get_millis
from constants import Subjects
from maths import clamp
from status import Status


# --------------------------------------------------------------------
@dataclass
class Resolution:
    width: int
    height: int

    @classmethod
    def by_aspect_ratio(cls, width: int, height: int, max_width: int = 10000):
        for x in range(width, max_width + 1):
            if x % 5 == 0:
                y = x / width * height
                if y.is_integer() and y % 5 == 0:
                    yield Resolution(x, int(y))


# --------------------------------------------------------------------
class MediaContainer:
    pad_x = 0
    pad_y = 0
    aspect_x = 16
    aspect_y = 9
    visible = True
    size = 10
    allow_focus = False
    adj_inc = 1
    adj_ms = 0

    window: Optional[Window] = None

    @classmethod
    def get_resolutions(cls) -> list[Resolution]:
        return [*Resolution.by_aspect_ratio(cls.aspect_x, cls.aspect_y)]

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
            window = cls.window
            cls.window = None

            if unfloat:
                window.floating = False
            if focus:
                window.focus(True)

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
    def _adj_ratio(cls, adj) -> int:
        now_ms = get_millis()
        if now_ms - cls.adj_ms < 50:
            cls.adj_inc += 1
        else:
            cls.adj_inc = 1
        cls.adj_ms = now_ms
        return cls.adj_inc * adj

    @classmethod
    def adjust_size(cls, adj: int):
        def _adjust_size(qtile: Qtile):
            cls.size = clamp(0, len(cls.get_resolutions()), cls.size + adj)
            cls.position_media_window(qtile, True)

        return _adjust_size

    @classmethod
    def adjust_pad_x(cls, adj: int):
        def _adjust_pad_x(qtile: Qtile):
            cls.pad_x = max(0, cls.pad_x + cls._adj_ratio(adj))
            cls.position_media_window(qtile, True)

        return _adjust_pad_x

    @classmethod
    def adjust_pad_y(cls, adj: int):
        def _adjust_pad_y(qtile: Qtile):
            cls.pad_y = max(0, cls.pad_y + cls._adj_ratio(adj))
            cls.position_media_window(qtile, True)

        return _adjust_pad_y

    @classmethod
    def adjust_opacity(cls, delta: float):
        def _adjust_opacity(qtile: Qtile):
            assert cls.window is not None
            cls.window.opacity = clamp(
                0.1, 1.0, cls.window.opacity + cls._adj_ratio(delta)
            )

        return _adjust_opacity

    @classmethod
    def position_media_window(cls, qtile: Qtile, print_status=False):
        assert cls.window is not None

        if not cls.visible:
            cls.window.minimized = True
            return

        cls.window.minimized = False

        res = cls.get_resolutions()[cls.size]
        cls.pad_x = clamp(
            0,
            qtile.current_screen.width - res.width,
            cls.pad_x,
        )
        cls.pad_y = clamp(
            0,
            qtile.current_screen.height - res.height,
            cls.pad_y
        )
        offset_x = qtile.current_screen.x + qtile.current_screen.width - res.width - cls.pad_x
        offset_y = qtile.current_screen.y + cls.pad_y

        cls.window.cmd_set_size_floating(res.width, res.height)
        cls.window.cmd_set_position_floating(offset_x, offset_y)
        cls.window.cmd_bring_to_front()

        if print_status:
            Status.show(
                Subjects.WINDOW_SIZE,
                f"{res.width}x{res.height} {cls.pad_x}x{cls.pad_y}y",
            )

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
    def focus_media(cls, qtile):
        assert cls.window is not None
        cls.allow_focus = True
        cls.window.focus(True)

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
                if cls.allow_focus:
                    cls.allow_focus = False
                else:
                    cls.focus_last_non_floating_window(qtile)
