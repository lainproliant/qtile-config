# --------------------------------------------------------------------
# module.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Wednesday May 6, 2020
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------

"""
Lain's Qtile configuration.

The functions below define values which are injected into the global namespace
and consumed by Qtile after dependency resolution.
"""

import subprocess
from pathlib import Path
from typing import List

from libqtile import bar, hook, layout, widget
from libqtile.config import Click, Drag, Group, Key, Screen
from libqtile.lazy import lazy

from framework import config, config_set, setup, inject


# -------------------------------------------------------------------
def util(cmd: str) -> str:
    return str(Path.home() / ".util" / cmd)


# -------------------------------------------------------------------
@config
def groups() -> List[Group]:
    return [Group(str(i)) for i in range(1, 10)]


# -------------------------------------------------------------------
@config
def mod() -> str:
    return "mod1"


# -------------------------------------------------------------------
@config
def keys(mod, groups) -> List[Key]:
    keys = [
        # --> Pane navigation commands.
        Key([mod], "j", lazy.layout.down()),
        Key([mod], "k", lazy.layout.up()),
        Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
        Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
        # --> Window state commands.
        Key([mod], "t", lazy.window.toggle_floating()),
        Key([mod], "f", lazy.window.toggle_fullscreen()),
        Key([mod, "shift"], "c", lazy.window.kill()),
        # --> Layout navigation commands.
        Key([mod], "h", lazy.layout.previous()),
        Key([mod], "l", lazy.layout.next()),
        Key([mod], "space", lazy.layout.rotate()),
        Key([mod, "shift"], "space", lazy.next_layout()),
        Key([mod, "shift"], "t", lazy.layout.toggle_split()),
        # --> Spawn commands
        Key([mod], "Return", lazy.spawncmd()),
        Key([mod, "shift"], "Return", lazy.spawn(util("terminal"))),
        # --> Process commands
        Key([mod], "q", lazy.restart()),
        Key([mod, "shift"], "q", lazy.shutdown()),
    ]

    for group in groups:
        keys.extend(
            [
                # mod1 + letter of group = switch to group
                Key([mod], group.name, lazy.group[group.name].toscreen()),
                Key([mod, "shift"], group.name, lazy.window.togroup(group.name)),
            ]
        )

    return keys


# -------------------------------------------------------------------
@config
def mouse(mod):
    """ Drag floating layouts. """
    return [
        Drag(
            [mod],
            "Button1",
            lazy.window.set_position_floating(),
            start=lazy.window.get_position(),
        ),
        Drag(
            [mod],
            "Button3",
            lazy.window.set_size_floating(),
            start=lazy.window.get_size(),
        ),
        Click([mod], "Button2", lazy.window.bring_to_front()),
    ]


# -------------------------------------------------------------------
@config
def layouts():
    return [
        layout.Max(),
        layout.Stack(num_stacks=2),
        # Try more layouts by unleashing below layouts.
        # layout.Bsp(),
        # layout.Columns(),
        # layout.Matrix(),
        # layout.MonadTall(),
        # layout.MonadWide(),
        # layout.RatioTile(),
        # layout.Tile(),
        # layout.TreeTab(),
        # layout.VerticalTile(),
        # layout.Zoomy(),
    ]


# -------------------------------------------------------------------
@config
def widget_defaults() -> dict:
    return {"font": "Iosevka Slab Regular", "fontsize": 16, "padding": 3}


# -------------------------------------------------------------------
@config
def extension_defualts(widget_defaults):
    return widget_defaults.copy()


# -------------------------------------------------------------------
@config
def screens():
    return [
        Screen(
            top=bar.Bar(
                [
                    widget.GroupBox(),
                    widget.sep.Sep(),
                    widget.CurrentLayout(),
                    widget.sep.Sep(),
                    widget.Prompt(),
                    widget.WindowName(),
                    widget.Systray(),
                    widget.sep.Sep(),
                    widget.Clock(format="%Y-%m-%d %a %H:%M:%S"),
                ],
                24,
            ),
        ),
    ]


# -------------------------------------------------------------------
@config
def floating_layout():
    return layout.Floating(
        float_rules=[
            # Run the utility of `xprop` to see the wm class and name of an X client.
            {"wmclass": "Guake"},
            {"wmclass": "Conky"},
            {"wmclass": "confirm"},
            {"wmclass": "dialog"},
            {"wmclass": "download"},
            {"wmclass": "error"},
            {"wmclass": "file_progress"},
            {"wmclass": "notification"},
            {"wmclass": "splash"},
            {"wmclass": "ssh-askpass"},  # ssh-askpass
            {"wmclass": "toolbar"},
            {"wname": "pinentry"},  # GPG key password entry
        ],
        border_width=0,
    )


# -------------------------------------------------------------------
@config_set
def other_settings():
    return {
        "auto_fullscreen": True,
        "bring_front_click": True,
        "cursor_warp": True,
        "dgroups_app_rules": [],
        "dgroups_key_binder": None,
        "focus_on_window_activation": "smart",
        "follow_mouse_focus": False,
        "main": None,
        "wmname": "LG3D",
    }


# -------------------------------------------------------------------
@setup
def setup_hooks():
    @hook.subscribe.startup_once
    def autostart():
        subprocess.call(str(Path.home() / ".xinit" / "twm-common"))

    @hook.subscribe.client_new
    def floating_dialogs(window):
        dialog = window.window.get_wm_type() == "dialog"
        transient = window.window.get_wm_transient_for()
        if dialog or transient:
            window.floating = True


# -------------------------------------------------------------------
inject(globals())
