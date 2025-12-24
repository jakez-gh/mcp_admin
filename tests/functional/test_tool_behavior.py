from mcp_admin.tools.registry import discover_tools, get_label_path, toggle_tool


def test_toggle_tool_updates_enabled_state() -> None:
    definitions = [{"name": "echo", "label": "Echo", "enabled": True}]
    root = discover_tools(definitions)

    assert toggle_tool(root, "echo", False) is True
    assert root.children[0].enabled is False


def test_label_navigation_returns_full_path() -> None:
    definitions = [
        {
            "name": "messaging",
            "label": "Messaging",
            "children": [{"name": "echo", "label": "Echo"}],
        }
    ]
    root = discover_tools(definitions)

    labels = get_label_path(root, "echo")

    assert labels == ["Root", "Messaging", "Echo"]
