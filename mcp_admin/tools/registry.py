from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass
class ToolNode:
    name: str
    label: str
    enabled: bool = True
    children: List["ToolNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "enabled": self.enabled,
            "children": [child.to_dict() for child in self.children],
        }


def _build_node(definition: dict) -> ToolNode:
    return ToolNode(
        name=definition["name"],
        label=definition.get("label", definition["name"].title()),
        enabled=definition.get("enabled", True),
        children=[_build_node(child) for child in definition.get("children", [])],
    )


def discover_tools(definitions: List[dict]) -> ToolNode:
    root = ToolNode(name="root", label="Root", enabled=True)
    root.children = [_build_node(definition) for definition in definitions]
    return root


def iter_tree(root: ToolNode) -> Iterable[ToolNode]:
    yield root
    for child in root.children:
        yield from iter_tree(child)


def find_tool(root: ToolNode, name: str) -> Optional[ToolNode]:
    for node in iter_tree(root):
        if node.name == name:
            return node
    return None


def toggle_tool(root: ToolNode, name: str, enabled: bool) -> bool:
    node = find_tool(root, name)
    if not node:
        return False
    node.enabled = enabled
    return True


def get_label_path(root: ToolNode, name: str) -> List[str]:
    def walk(node: ToolNode, labels: List[str]) -> Optional[List[str]]:
        if node.name == name:
            return labels + [node.label]
        for child in node.children:
            result = walk(child, labels + [node.label])
            if result:
                return result
        return None

    result = walk(root, [])
    return result or []
