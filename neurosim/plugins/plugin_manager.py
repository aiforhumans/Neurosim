"""
Plugin management for NeuroSim.

This module defines a simple plugin architecture that allows
additional behaviours to be registered and executed when messages are
processed. Plugins live in the ``neurosim/plugins`` package and
should define a subclass of :class:`BasePlugin` with an
``on_message`` method. The plugin manager will discover and
instantiate these classes on startup.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional


class BasePlugin:
    """Base class for plugins. Override :meth:`on_message` in subclasses."""

    def on_message(self, message: str, session_state) -> Optional[str]:  # noqa: ANN001
        """
        Hook called when a message is processed.

        Args:
            message: The raw user message.
            session_state: The current session state.

        Returns:
            Optionally return a replacement response. If ``None`` is returned
            the next plugin (or core logic) will handle the message.
        """
        return None


class PluginManager:
    """Discover and manage installed plugins."""

    def __init__(self) -> None:
        self.plugins: List[BasePlugin] = []
        self.load_plugins()

    def load_plugins(self) -> None:
        """Discover and instantiate plugins in the ``neurosim.plugins`` package."""
        package_name = __package__.split(".")[0]  # 'neurosim'
        plugins_pkg = f"{package_name}.plugins"
        # Iterate through all modules in the plugins package
        for _, module_name, is_pkg in pkgutil.iter_modules([str(Path(__file__).resolve().parent)]):
            if is_pkg or module_name == "plugin_manager":
                continue
            full_name = f"{plugins_pkg}.{module_name}"
            try:
                module = importlib.import_module(full_name)
            except Exception:
                # Skip modules that fail to import
                continue
            # Find subclasses of BasePlugin in the module
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    try:
                        instance = obj()
                        self.plugins.append(instance)
                    except Exception:
                        continue

    def run_plugins(self, message: str, session_state) -> Optional[str]:  # noqa: ANN001
        """
        Run all plugins on the message and return the first non-None response.

        Args:
            message: The raw user message.
            session_state: The current session state.

        Returns:
            The response from a plugin if any plugin handles the message; otherwise
            ``None``.
        """
        for plugin in self.plugins:
            try:
                result = plugin.on_message(message, session_state)
                if result is not None:
                    return result
            except Exception:
                # Ignore plugin errors and continue to the next plugin
                continue
        return None