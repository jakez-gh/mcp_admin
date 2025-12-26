from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class ToolNode:
    name: str
    label: str
    enabled: bool = True
    children: list[ToolNode] = field(default_factory=list)

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


def discover_tools(definitions: list[dict]) -> ToolNode:
    root = ToolNode(name="root", label="Root", enabled=True)
    root.children = [_build_node(definition) for definition in definitions]
    return root


def iter_tree(root: ToolNode) -> Iterable[ToolNode]:
    yield root
    for child in root.children:
        yield from iter_tree(child)


def find_tool(root: ToolNode, name: str) -> ToolNode | None:
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


def get_label_path(root: ToolNode, name: str) -> list[str]:
    def walk(node: ToolNode, labels: list[str]) -> list[str] | None:
        if node.name == name:
            return labels + [node.label]
        for child in node.children:
            result = walk(child, labels + [node.label])
            if result:
                return result
        return None

    result = walk(root, [])
    return result or []
