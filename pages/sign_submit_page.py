"""SignSubmitPage page object for the Sign & Submit multi-step flow."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class SignSubmitPage(BasePage):
    """Page object for the 'Sign & Submit' multi-sub-page flow.

    The sign/submit flow on the VFA site has these sub-pages:
      1. Delivery method — click "Email directly to you"
      2. Email reminder + Next
      3. Send Email button
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def skip_signature(self) -> None:
        """No-op — the signature step is not shown in the current flow."""
        pass

    def select_email_delivery(self) -> None:
        """Click 'Email directly to you' and decline email reminder."""
        # Wait for the email delivery sub-page to render
        self.page.locator("#id_sign_submit_nextsteps_emailtovoter").wait_for(
            state="visible", timeout=self.PAGE_TRANSITION_TIMEOUT
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
