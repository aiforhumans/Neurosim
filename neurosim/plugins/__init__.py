"""
Plugin system for NeuroSim.

Plugins allow developers to extend the behaviour of agents without
modifying core code. Each plugin should define a class deriving from
``BasePlugin`` and implement the ``on_message`` hook. Plugins are
loaded from the ``neurosim/plugins`` directory at runtime.
"""

from .plugin_manager import PluginManager, BasePlugin  # noqa: F401