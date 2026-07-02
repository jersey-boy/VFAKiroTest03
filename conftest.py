"""pytest configuration with custom Playwright fixtures.

Uses a custom page fixture instead of pytest-playwright's built-in one
to avoid plugin interference with Vue SPA form interactions.
"""
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser_instance():
    """Launch a browser instance for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser_instance):
    """Create a fresh page/context for each test."""
    context = browser_instance.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    yield page
    context.close()
