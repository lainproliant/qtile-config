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

from libqtile import bar, hook, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.core.manager import Qtile
from libqtile.lazy import lazy

from base16 import Base16
from constants import FONT_SCALING_RATIO, Subjects
from framework import config, config_set, inject, provide, setup
from media import MediaContainer
from status import Status
from util import (
    adjust_opacity,
    ground_all_floats,
    window_to_next_screen,
    window_to_prev_screen,
)
from widget import CustomMemory, CustomNetwork, FastGenPollText


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
        info = json.load(infile)
        info["original"] = info["font"]
        info["info"] = "Overpass"
        info["font"] = "Overpass Mono"
        return info


# -------------------------------------------------------------------
@provide
def base16() -> Base16:
    return Base16.load_from_xdefaults()


# -------------------------------------------------------------------
@config
def groups(circle_numbers) -> List[Group]:
    return [Group(str(i), label=circle_numbers[i]) for i in range(1, 10)]


# -------------------------------------------------------------------
@config
def mod() -> str:
    return "mod4"


# -------------------------------------------------------------------
@config
def keys(mod, groups) -> List[Key]:
    keys = [
        # --> Navigation commands.
        Key([mod], "j", lazy.layout.next()),
        Key([mod], "k", lazy.layout.previous()),
        Key([mod, "shift"], "h", lazy.layout.shuffle_left()),
        Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
        Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
        Key([mod, "shift"], "l", lazy.layout.shuffle_right()),
        Key([mod], "h", lazy.layout.left()),
        Key([mod], "l", lazy.layout.right()),
        Key([mod], "e", lazy.prev_screen()),
        Key([mod], "w", lazy.next_screen()),
        # --> Window state commands.
        Key([mod], "f", lazy.window.toggle_floating()),
        Key([mod, "shift"], "c", lazy.window.kill()),
        Key([mod, "shift"], "e", lazy.function(window_to_next_screen)),
        Key([mod, "shift"], "f", lazy.window.toggle_fullscreen()),
        Key([mod, "shift"], "g", lazy.function(ground_all_floats)),
        Key([mod, "shift", "control"], "v", lazy.function(MediaContainer.focus_media)),
        Key([mod, "shift"], "v", lazy.function(MediaContainer.toggle_media)),
        Key([mod, "shift"], "w", lazy.function(window_to_prev_screen)),
        Key([mod], "b", lazy.function(adjust_opacity(0.01))),
        Key([mod, "shift"], "b", lazy.function(adjust_opacity(-0.01))),
        # --> Media window controls
        Key([mod], "v", lazy.function(MediaContainer.media_front_toggle)),
        Key([mod], "slash", lazy.function(MediaContainer.adjust_size(1))),
        Key(
            [mod, "shift"],
            "slash",
            lazy.function(MediaContainer.adjust_size(-1)),
        ),
        Key([mod], "semicolon", lazy.function(MediaContainer.adjust_pad_x(1))),
        Key(
            [mod, "shift"],
            "semicolon",
            lazy.function(MediaContainer.adjust_pad_x(-1)),
        ),
        Key([mod], "apostrophe", lazy.function(MediaContainer.adjust_pad_y(1))),
        Key(
            [mod, "shift"],
            "apostrophe",
            lazy.function(MediaContainer.adjust_pad_y(-1)),
        ),
        # --> Layout modification commands.
        Key([mod, "shift"], "space", lazy.next_layout()),
        Key([mod], "space", lazy.layout.flip()),
        Key([mod], "r", lazy.layout.rotate()),
        Key([mod], "t", lazy.layout.toggle_split()),
        Key([mod], "backslash", lazy.layout.add()),
        Key([mod, "shift"], "backslash", lazy.layout.delete()),
        Key([mod], "period", lazy.layout.grow()),
        Key([mod], "comma", lazy.layout.shrink()),
        # --> Spawn commands.
        Key([mod], "Return", lazy.spawn(util("program_menu"))),
        Key([mod], "Escape", lazy.spawn(util("lock"))),
        Key([mod, "shift"], "Return", lazy.spawn(util("terminal"))),
        Key([mod, "shift"], "o", lazy.spawn(util("browser"))),
        Key([mod], "p", lazy.spawn(util("next_bg"))),
        Key([mod], "o", lazy.spawn(util("prev_bg"))),
        Key([mod, "shift"], "p", lazy.spawn(util("random_bg"))),
        Key([mod, "control"], "space", lazy.spawn(util("toggle_touchpad"))),
        Key([mod], "n", lazy.spawn(util("mouse1_hint"))),
        Key([mod], "m", lazy.spawn(util("mouse3_hint"))),
        Key([mod, "shift"], "n", lazy.spawn(util("mouse1_grid"))),
        Key([mod, "shift"], "m", lazy.spawn(util("mouse3_grid"))),
        Key([mod, "control"], "n", lazy.spawn(util("mouse1_normal"))),
        Key([mod, "control"], "m", lazy.spawn(util("mouse3_normal"))),
        # --> Qtile process commands.
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
    return dict(border_width=2, border_focus=base16(0x05), border_normal=base16(0x00))


# -------------------------------------------------------------------
@config
def layouts(borders):
    return [
        layout.Max(name="max"),
        layout.Columns(name="col", **borders),
        layout.xmonad.MonadTall(name="mt", **borders),
        layout.xmonad.MonadWide(name="mw", **borders),
        # Try more layouts by unleashing below layouts.
        # layout.Bsp(),
        # layout.Matrix(),
        # layout.RatioTile(),
        # layout.Stack(num_stacks=1, name="stk", **borders),
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
        fontsize=font_info["size"] + 8,
        padding=1,
        background=base16(0x00),
        foreground=base16(0x05),
    )


# -------------------------------------------------------------------
@config
def extension_defaults(widget_defaults):
    return widget_defaults.copy()


# -------------------------------------------------------------------
@provide
def circle_numbers():
    return "0❶❷❸❹❺❻❼❽❾"


# -------------------------------------------------------------------
@provide
def sep_factory(base16: Base16) -> Callable[[], widget.Sep]:
    def factory():
        return widget.Sep(padding=16, foreground=base16(0x03))

    return factory


# -------------------------------------------------------------------
@provide
def battery_widget(font_info) -> widget.Battery:
    return widget.Battery(
        format="{char}{percent:2.0%}",
        charge_char="+",
        discharge_char="-",
        empty_char="XX",
    )


# -------------------------------------------------------------------
@provide
def group_box_factory(
    base16: Base16, font_info, widget_defaults
) -> Callable[[], widget.GroupBox]:
    def factory():
        return widget.GroupBox(
            highlight_method="text",
            hide_unused=True,
            active=base16(0x03),
            inactive=base16(0x03),
            this_current_screen_border=base16(0x07),
            this_screen_border=base16(0x0E),
            other_screen_current_border=base16(0x01),
            other_screen_border=base16(0x01),
        )

    return factory


# -------------------------------------------------------------------
@config
def screens(
    base16: Base16,
    num_screens,
    widget_defaults,
    battery_widget,
    group_box_factory,
    sep_factory,
    font_info,
):
    scaled_fontsize = int(font_info["size"] * FONT_SCALING_RATIO)
    bar_height = scaled_fontsize + 16
    MediaContainer.bar_height = bar_height

    return [
        Screen(
            top=bar.Bar(
                [
                    group_box_factory(),
                    sep_factory(),
                    widget.WindowName(
                        width=bar.STRETCH,
                        empty_group_string="(empty)",
                        font=font_info["info"],
                        fontsize=scaled_fontsize,
                    ),
                    sep_factory(),
                    FastGenPollText(
                        func=Status.update,
                        update_interval=Status.update_sec,
                        fontsize=scaled_fontsize,
                    ),
                    sep_factory(),
                    CustomNetwork(
                        font=font_info["info"],
                        fontsize=scaled_fontsize,
                        foreground=base16(0x03),
                    ),
                    sep_factory(),
                    CustomMemory(fontsize=scaled_fontsize, foreground=base16(0x03)),
                    widget.CPU(
                        format="@{load_percent:02.0f}% ",
                        fontsize=scaled_fontsize,
                        foreground=base16(0x03),
                    ),
                    battery_widget,
                    sep_factory(),
                    widget.Clock(
                        format="%a ", fontsize=scaled_fontsize, foreground=base16(0x03)
                    ),
                    widget.Clock(
                        format="%m/%d/%Y ",
                        fontsize=scaled_fontsize,
                        foreground=base16(0x03),
                    ),
                    widget.Clock(format="%H:%M:%S"),
                ],
                size=bar_height,
                **widget_defaults,
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
        "bring_front_click": False,
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
    MediaContainer.setup_hooks()

    @hook.subscribe.startup_once
    def autostart():
        subprocess.call(str(Path.home() / ".xinit" / "twm-common"))

    @hook.subscribe.client_new
    def floating_dialogs(window):
        # Automatically make mpv windows the media window.
        auto_media_rules = [Match(wm_class="mpv")]
        if any(window.match(rule) for rule in auto_media_rules):
            MediaContainer.set_media(qtile, window)
            qtile.call_later(0, MediaContainer.position_media_window, qtile)

        dialog = window.window.get_wm_type() == "dialog"
        transient = window.window.get_wm_transient_for()
        if dialog or transient:
            window.floating = True

    @hook.subscribe.layout_change
    def on_layout_change(layout, group):
        Status.show(Subjects.LAYOUT, str(layout.name))

    @hook.subscribe.setgroup
    def on_group_changed():
        assert isinstance(qtile, Qtile)
        if qtile.current_group.name == "9":
            qtile.current_screen.top.show(False)
        else:
            qtile.current_screen.top.show(True)


# -------------------------------------------------------------------
inject(globals())
