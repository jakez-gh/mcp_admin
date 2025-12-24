from __future__ import annotations

import contextlib
import functools
import http.server
import socketserver
import threading
from pathlib import Path
from typing import Iterator

import pytest

playwright = pytest.importorskip("playwright.sync_api")


@contextlib.contextmanager
def run_ui_server() -> Iterator[str]:
    ui_dir = Path(__file__).resolve().parents[2] / "mcp_admin" / "ui"

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ui_dir))

    class QuietTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{port}/index.html"
        finally:
            httpd.shutdown()
            thread.join(timeout=2)


def test_admin_ui_toggle_and_labels() -> None:
    from playwright.sync_api import sync_playwright

    with run_ui_server() as ui_url:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(ui_url)

            page.get_by_test_id("toggle-echo").click()
            status = page.get_by_test_id("status-echo").text_content()
            assert status == "Disabled"

            page.get_by_test_id("next-label").click()
            label = page.get_by_test_id("label-current").text_content()
            assert label == "Messaging"

            browser.close()


def test_admin_ui_label_cycles_to_leaf() -> None:
    from playwright.sync_api import sync_playwright

    with run_ui_server() as ui_url:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(ui_url)

            page.get_by_test_id("next-label").click()
            page.get_by_test_id("next-label").click()
            label = page.get_by_test_id("label-current").text_content()
            assert label == "Echo"

            browser.close()
