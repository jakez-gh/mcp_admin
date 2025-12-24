from __future__ import annotations

import importlib
import pkgutil
from typing import Iterable, List, Type

from server.tools.base import BaseTool


def discover_tool_classes(package: str = "server.tools") -> List[Type[BaseTool]]:
    tool_classes: List[Type[BaseTool]] = []
    package_module = importlib.import_module(package)

    for module_info in pkgutil.iter_modules(package_module.__path__, package_module.__name__ + "."):
        module = importlib.import_module(module_info.name)
        for attribute in vars(module).values():
            if isinstance(attribute, type) and issubclass(attribute, BaseTool) and attribute is not BaseTool:
                tool_classes.append(attribute)

    return tool_classes


def instantiate_tools(package: str = "server.tools") -> List[BaseTool]:
    return [tool_class() for tool_class in discover_tool_classes(package)]


def iter_tools(package: str = "server.tools") -> Iterable[BaseTool]:
    for tool in instantiate_tools(package):
        yield tool
