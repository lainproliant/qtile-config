# --------------------------------------------------------------------
# util.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Tuesday August 16, 2022
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------

from libqtile.core.manager import Qtile
from media import MediaContainer


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
def ground_all_floats(qtile: Qtile):
    """
    Bring all floating windows in the current group back into
    the tiling layout.
    """
    for window in qtile.current_group.windows:
        if window.floating and window is not MediaContainer.window:
            window.toggle_floating()


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
