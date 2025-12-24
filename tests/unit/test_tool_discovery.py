from mcp_admin.tools.registry import discover_tools, find_tool


def test_discover_tools_builds_hierarchy() -> None:
    definitions = [
        {
            "name": "messaging",
            "label": "Messaging",
            "children": [{"name": "echo", "label": "Echo"}],
        }
    ]

    root = discover_tools(definitions)

    assert root.name == "root"
    assert len(root.children) == 1
    assert root.children[0].name == "messaging"
    assert root.children[0].children[0].label == "Echo"


def test_find_tool_returns_nested_node() -> None:
    definitions = [
        {
            "name": "analytics",
            "label": "Analytics",
            "children": [{"name": "report", "label": "Report"}],
        }
    ]
    root = discover_tools(definitions)

    found = find_tool(root, "report")

    assert found is not None
    assert found.name == "report"
