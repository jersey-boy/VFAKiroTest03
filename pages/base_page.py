"""Base page object with shared utilities for all page objects."""

from playwright.sync_api import Page


# Timeout constants (milliseconds)
PAGE_TRANSITION_TIMEOUT = 15_000
FIELD_INTERACTION_TIMEOUT = 5_000


class BasePage:
    """Base class for all page objects providing shared navigation utilities."""

    PAGE_TRANSITION_TIMEOUT = PAGE_TRANSITION_TIMEOUT
    FIELD_INTERACTION_TIMEOUT = FIELD_INTERACTION_TIMEOUT

    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_for_url_contains(self, path: str) -> None:
        """Wait for the page URL to contain the given path segment.

        Uses polling since the SPA uses Vue Router pushState (no navigation event).
        """
        self.page.wait_for_function(
            f"() => window.location.href.includes('{path}')",
            timeout=self.PAGE_TRANSITION_TIMEOUT,
        )

    def click_next_button(self) -> None:
        """Click the visible Next button to advance to the next form step.

        The VFA site uses different button ID patterns on different pages:
        - Steps 1-3: id_pages_request_stage_next_01/02/03
        - Steps 4-5: id_sign_submit_nextsteps_next_01/02/etc.
        """
        next_btn = self.page.locator(
            'button:visible:has-text("Next >>")'
        )
        next_btn.scroll_into_view_if_needed()
        next_btn.click()
