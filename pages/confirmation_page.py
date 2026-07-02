"""ConfirmationPage page object for verifying successful form submission."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class ConfirmationPage(BasePage):
    """Page object for the confirmation/success page after FPCA submission."""

    CONFIRMATION_KEYWORDS = ("submitted", "complete", "confirmation", "sent", "thank")

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def verify_success(self) -> None:
        """Verify the confirmation page contains success-related text."""
        body_text = self.page.locator("body").text_content(
            timeout=self.PAGE_TRANSITION_TIMEOUT
        )
        if body_text is None:
            raise AssertionError("Could not read page content after submission.")

        body_lower = body_text.lower()
        for keyword in self.CONFIRMATION_KEYWORDS:
            if keyword in body_lower:
                return

        raise AssertionError(
            f"Confirmation page did not contain expected keywords. "
            f"Expected one of: {self.CONFIRMATION_KEYWORDS}"
        )
