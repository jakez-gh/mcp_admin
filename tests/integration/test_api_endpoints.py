from fastapi.testclient import TestClient

from mcp_admin.api import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tools_returns_children() -> None:
    client = TestClient(create_app())

    response = client.get("/tools")

    assert response.status_code == 200
    payload = response.json()
    assert "tools" in payload
    assert payload["tools"][0]["name"] == "messaging"


def test_toggle_tool_endpoint() -> None:
    client = TestClient(create_app())

    response = client.post("/tools/echo/enable", json={"enabled": False})

    assert response.status_code == 200
    assert response.json() == {"name": "echo", "enabled": False}


def test_tool_label_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/tools/echo/labels")

    assert response.status_code == 200
    assert response.json()["labels"][-1] == "Echo"


def test_toggle_tool_endpoint_returns_404_for_missing_tool() -> None:
    client = TestClient(create_app())

    response = client.post("/tools/missing/enable", json={"enabled": True})

    assert response.status_code == 404


def test_tool_label_endpoint_returns_404_for_missing_tool() -> None:
    client = TestClient(create_app())

    response = client.get("/tools/missing/labels")

    assert response.status_code == 404
