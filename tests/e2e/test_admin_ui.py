from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")


def test_admin_ui_toggle_and_labels() -> None:
    from playwright.sync_api import sync_playwright

    html_path = Path(__file__).resolve().parents[2] / "mcp_admin" / "ui" / "index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri())

        page.get_by_test_id("toggle-echo").click()
        status = page.get_by_test_id("status-echo").text_content()
        assert status == "Disabled"

        page.get_by_test_id("next-label").click()
        label = page.get_by_test_id("label-current").text_content()
        assert label == "Messaging"

        browser.close()
