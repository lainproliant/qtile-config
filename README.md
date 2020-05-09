# Lain's Qtile Configs

These are my personal configs for Qtile, the python-based tiling window manager.

I wanted a more "functional" configuration, so I brought in the
[Xeno](https://github.com/lainproliant/xeno) (my DI framework) to let me define
config options as functional resources dependent on each other and on other
runtime-determined things, e.g. the number of monitors currently being
displayed, or certain devices connected at runtime.  While this can all be done
with a classic flat config, I chose this path because it lets me quickly
iterate and keeps the configuration clean and modular.  Also, I just like it
this way and aesthetics are important :)

## Requirements
- `xeno>=4.3.0`: Used for dependency injection.
    - See `https://github.com/lainproliant/xeno`.
- Iosevka Fonts
    - In Arch Linux, these can be acquired via `ttf-iosevka`.

## Setup
1. Clone or add the repo as a submodule to your main config repo.
    - `git clone https://github.com/lainproliant/qtile-config ~/.config/qtile`
    - OR `cd ~/.dotfiles/config; git submodule add https://github.com/lainproliant/qtile-config qtile`
2. Install the dependencies.
    - `cd qtile; pip install -r requirements.txt`
3. Restart qtile.

## Assumptions
Most of my dotfiles aren't made public.  This configuration makes some
assumptions about your dotfiles and system setup:

- We assume there is a `~/.util` directory full of utility scripts, which
  can be found at `https://github.com/lainproliant/util-scripts`.
- We assume the presence of `~/.xinit/twm-common`, a setup script.  I use this
  script to start various programs.  This can be found at
  `https://github.com/lainproliant/xinit-scripts`.

## Final Notes
These scripts are opinionated but I'm not.  Do whatever you want with this, and
most importantly: have fun!
