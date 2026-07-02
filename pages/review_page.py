"""ReviewPage page object for the Review form step."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class ReviewPage(BasePage):
    """Page object for the 'Review' step (Step 4) of the FPCA form.

    This step just displays a summary — no interaction needed except clicking Next.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def verify_summary_displayed(self) -> None:
        """No-op — the review page is just a pass-through."""
        self.page.wait_for_timeout(500)

    def click_next(self) -> None:
        """Click Next to advance to the Sign & Submit flow."""
        self.page.locator("#id_sign_submit_nextsteps_next_01").click()
        self.page.wait_for_timeout(1000)
        self.page.wait_for_timeout(2000)  # Wait for Sign & Submit sub-page to render
