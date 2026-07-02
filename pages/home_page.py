"""HomePage page object for the VFA landing page."""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage


class HomePage(BasePage):
    """Page object for the VoteFromAbroad homepage."""

    URL = "https://vfa-newux.netlify.app/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def navigate(self) -> None:
        """Navigate to the VFA homepage."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def dismiss_cookie_banner(self) -> None:
        """Dismiss the cookie consent banner by clicking 'Accept All'.

        If the banner does not appear within 5 seconds, proceeds without error.
        """
        try:
            accept_button = self.page.get_by_text("Accept All")
            accept_button.click(timeout=self.FIELD_INTERACTION_TIMEOUT)
        except PlaywrightTimeoutError:
            # Banner didn't appear within timeout — proceed normally
            pass

    def click_request_ballot(self) -> None:
        """Click the 'Request your ballot' button and verify navigation.

        Waits for the page to navigate to the Your Information step.
        """
        self.page.locator("#btn_landing_page").click()
        self.wait_for_url_contains("/request/your-information")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)  # Allow Vue components to mount
