import unittest

from server.mcp_registry import MCPRegistry
from server.tool_loader import discover_tool_classes, instantiate_tools
from server.tools.example_tool import ExampleEchoTool


class ToolDiscoveryTests(unittest.TestCase):
    def test_discover_tool_classes_finds_example(self) -> None:
        classes = discover_tool_classes()
        self.assertIn(ExampleEchoTool, classes)

    def test_instantiate_tools_returns_examples(self) -> None:
        tools = instantiate_tools()
        tool_names = {tool.metadata.name for tool in tools}
        self.assertIn("example.echo", tool_names)

    def test_registry_registers_tools(self) -> None:
        registry = MCPRegistry()
        registry.register_many(instantiate_tools())
        listed = registry.list_tools()
        names = {tool["name"] for tool in listed}
        self.assertIn("example.echo", names)


if __name__ == "__main__":
    unittest.main()
