# --------------------------------------------------------------------
# framework.py
#
# Author: Lain Musgrove (lain.proliant@gmail.com)
# Date: Wednesday May 6, 2020
#
# Distributed under terms of the MIT license.
# --------------------------------------------------------------------

"""
Provides a Xeno-powered framework to allow Qtile settings to be
defined as functions and injected into the config namespace
after dependency resolution.
"""

from typing import Set
from xeno import MethodAttributes, SyncInjector


# -------------------------------------------------------------------
injector = SyncInjector()
provide = injector.provide


# -------------------------------------------------------------------
def config(f):
    attrs = MethodAttributes.for_method(f, write=True)
    attrs.put("qtile_config")
    return provide(f)


# -------------------------------------------------------------------
def config_set(f):
    attrs = MethodAttributes.for_method(f, write=True)
    attrs.put("qtile_config_set")
    return provide(f)


# -------------------------------------------------------------------
def setup(f):
    attrs = MethodAttributes.for_method(f, write=True)
    attrs.put("qtile_setup")
    return provide(f)


# -------------------------------------------------------------------
def _scan(injector: SyncInjector, target_attr: str) -> Set[str]:
    return {
        k for k, v in injector.scan_resources(lambda k, attrs: attrs.check(target_attr))
    }


# -------------------------------------------------------------------
def inject(namespace: dict, injector: SyncInjector = injector):
    for key in _scan(injector, "qtile_config"):
        namespace[key] = injector.require(key)

    for key in _scan(injector, "qtile_config_set"):
        config_set = injector.require(key)
        for k, v in config_set.items():
            namespace[k] = v

    for key in _scan(injector, "qtile_setup"):
        injector.require(key)
