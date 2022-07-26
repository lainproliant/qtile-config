# --------------------------------------------------------------------
# config.py
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

import json
import subprocess
from pathlib import Path
from typing import Callable, List

from libqtile import bar, hook, layout, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

from base16 import Base16
from framework import config, config_set, inject, provide, setup
from widget import CustomMemory, CustomNetwork


# -------------------------------------------------------------------
def util(cmd: str) -> str:
    return str(Path.home() / ".util" / cmd)


# -------------------------------------------------------------------
@provide
def num_screens() -> int:
    return int(
        subprocess.check_output(
            'xrandr | grep " connected " | wc -l', shell=True
        ).decode("utf-8")
    )


# -------------------------------------------------------------------
@provide
def font_info() -> dict:
    with open(Path.home() / ".font/config.json", "r") as infile:
        return json.load(infile)


# -------------------------------------------------------------------
@provide
def base16() -> Base16:
    return Base16.load_from_xdefaults()


# -------------------------------------------------------------------
@config
def groups() -> List[Group]:
    return [Group(str(i)) for i in range(1, 10)]


# -------------------------------------------------------------------
@config
def mod() -> str:
    return "mod4"


# -------------------------------------------------------------------
@config
def keys(mod, groups) -> List[Key]:
    keys = [
        # --> Pane navigation commands.
        Key([mod], "j", lazy.layout.down()),
        Key([mod], "k", lazy.layout.up()),
        Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
        Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
        Key([mod], "h", lazy.layout.previous()),
        Key([mod], "l", lazy.layout.next()),
        Key([mod, "shift"], "h", lazy.layout.client_to_previous()),
        Key([mod, "shift"], "l", lazy.layout.client_to_next()),
        Key([mod], "backslash", lazy.layout.add()),
        Key([mod, "shift"], "backslash", lazy.layout.delete()),
        # --> Window state commands.
        Key([mod], "f", lazy.window.toggle_fullscreen()),
        Key([mod, "shift"], "f", lazy.window.toggle_floating()),
        Key([mod, "shift"], "c", lazy.window.kill()),
        # --> Layout navigation commands.
        Key([mod], "space", lazy.layout.rotate()),
        Key([mod, "shift"], "space", lazy.next_layout()),
        Key([mod], "t", lazy.layout.toggle_split()),
        # --> Spawn commands
        Key([mod], "Return", lazy.spawn(util("program_menu"))),
        Key([mod, "shift"], "Return", lazy.spawn(util("terminal"))),
        Key([mod, "shift"], "o", lazy.spawn(util("browser"))),
        # --> Process commands
        Key([mod], "q", lazy.restart()),
        Key([mod, "shift"], "q", lazy.shutdown()),
    ]

    # mod1 + letter of group = switch to group
    for group in groups:
        keys.extend(
            [
                Key([mod], group.name, lazy.group[group.name].toscreen()),
                Key([mod, "shift"], group.name, lazy.window.togroup(group.name)),
            ]
        )

    return keys


# -------------------------------------------------------------------
@config
def mouse(mod):
    """Drag floating layouts."""
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
def borders(base16: Base16):
    return dict(border_focus=base16(0x05), border_normal=base16(0x00))


# -------------------------------------------------------------------
@config
def layouts(borders):
    return [
        layout.Max(name="[ ]"),
        layout.Stack(num_stacks=1, name="[|]", border_width=4, **borders),
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
def widget_defaults(font_info, base16: Base16) -> dict:
    return dict(
        font=font_info["font"],
        fontsize=font_info["size"],
        padding=1,
        background=base16(0x00),
        foreground=base16(0x05),
    )


# -------------------------------------------------------------------
@config
def extension_defualts(widget_defaults):
    return widget_defaults.copy()


# -------------------------------------------------------------------
@provide
def sep_factory() -> Callable[[], widget.Sep]:
    def factory():
        return widget.Sep(padding=16)

    return factory


# -------------------------------------------------------------------
@provide
def battery_widget() -> widget.Battery:
    return widget.Battery(
        format="{char}{percent:2.0%} ",
        charge_char="+",
        discharge_char="-",
        empty_char="XX",
    )


# -------------------------------------------------------------------
@provide
def group_box_factory(base16: Base16) -> Callable[[], widget.GroupBox]:
    def factory():
        return widget.GroupBox(
            highlight_method="block",
            background=base16(0x00),
            inactive=base16(0x03),
            this_current_screen_border=base16(0x08),
            this_screen_border=base16(0x0E),
            other_screen_current_border=base16(0x01),
            other_screen_border=base16(0x01),
        )

    return factory


# -------------------------------------------------------------------
@config
def screens(
    num_screens, widget_defaults, battery_widget, group_box_factory, sep_factory
):
    return [
        Screen(
            top=bar.Bar(
                [
                    group_box_factory(),
                    sep_factory(),
                    widget.CurrentLayout(),
                    sep_factory(),
                    widget.WindowName(),
                    CustomNetwork(),
                    sep_factory(),
                    CustomMemory(),
                    widget.CPU(format="@{load_percent:02.0f}% "),
                    battery_widget,
                    widget.Clock(format="%a %m/%d/%Y %H:%M:%S"),
                ],
                size=26,
                **widget_defaults
            ),
        )
        for screen in range(num_screens)
    ]


# -------------------------------------------------------------------
@config
def floating_layout():
    return layout.Floating(
        float_rules=[
            *layout.Floating.default_float_rules,
            # Run the utility of `xprop` to see the wm class and name of an X client.
            *[
                Match(wm_class=x)
                for x in [
                    "Guake",
                    "Conky",
                    "confirm",
                    "dialog",
                    "download",
                    "error",
                    "file_progress",
                    "notification",
                    "splash",
                    "ssh-askpass",
                    "toolbar",
                ]
            ],
            Match(title="pinentry"),
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
