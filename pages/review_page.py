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
        """Click Next to advance to the Sign & Submit flow.

        The review page has a Next button that navigates within the same URL
        (/request/sign-submit-nextsteps). We need to wait for the button to
        appear first since the page may still be rendering.
        """
        next_btn = self.page.locator("#id_sign_submit_nextsteps_next_01")
        next_btn.wait_for(state="visible", timeout=self.PAGE_TRANSITION_TIMEOUT)
        next_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
        next_btn.click()
        # Wait for the signature sub-page to fully render
        self.page.wait_for_timeout(2000)
