"""SignSubmitPage page object for the Sign & Submit multi-step flow."""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage


class SignSubmitPage(BasePage):
    """Page object for the 'Sign & Submit' multi-sub-page flow.

    The sign/submit flow on the VFA site varies based on voter category selected
    on Step 2:
      - "Intend to Return" and "Military": Skip signature → Email delivery
      - "Uncertain Return", "Never Resided", "Military Spouse": Signature choice
        → Email delivery

    Flow:
      1. (Conditional) Signature page — click "NO, I don't wish to attach..."
      2. Email delivery — click "Email directly to you"
      3. Email reminder — decline + Next
      4. Send Email button
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def skip_signature(self) -> None:
        """Click 'NO' to skip signature if the signature page appears.

        Some voter categories (intend to return, military) skip the signature
        step entirely. In that case, this method is a no-op.
        """
        try:
            no_sign_btn = self.page.locator("#id_sign_submit_nextsteps_04")
            no_sign_btn.wait_for(state="visible", timeout=5_000)
            no_sign_btn.click()
            self.page.wait_for_timeout(2000)
        except PlaywrightTimeoutError:
            # Signature page not shown (e.g., military or intend-to-return)
            pass

    def select_email_delivery(self) -> None:
        """Click 'Email directly to you' and decline email reminder."""
        # Wait for the email delivery sub-page to render
        self.page.locator("#id_sign_submit_nextsteps_emailtovoter").wait_for(
            state="visible", timeout=30_000
        )
        self.page.locator("#id_sign_submit_nextsteps_emailtovoter").click()
        self.page.wait_for_timeout(1000)
        # Decline email reminder
        self.page.locator("#rb_emailReminder_false").click()
        self.page.wait_for_timeout(300)

    def click_next(self) -> None:
        """Click Next to proceed to the final send page."""
        self.page.locator("#id_sign_submit_nextsteps_next_03").click()
        self.page.wait_for_timeout(2000)

    def click_send_email(self) -> None:
        """Click 'Send Email' to complete the submission."""
        self.page.locator("#id_SubmitComposeMessageToVoter").click()
        # Wait for the confirmation to appear
        self.page.wait_for_timeout(5000)
