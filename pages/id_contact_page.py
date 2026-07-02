"""IdContactPage page object for the ID and Contact Information form step."""

import random

from playwright.sync_api import Page

from data.generator import DateOfBirth
from pages.base_page import BasePage


class IdContactPage(BasePage):
    """Page object for the 'ID and Contact Information' step of the FPCA form."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def fill_dob(self, dob: DateOfBirth) -> None:
        """Select month, day, and year from the date of birth dropdowns."""
        self.page.wait_for_timeout(500)  # Wait for Step 3 to render
        self.page.locator("#optionsSelectMonth").select_option(label=dob.month)
        self.page.wait_for_timeout(300)
        # Day options are zero-padded (01, 02, ... 31)
        day_str = str(dob.day).zfill(2)
        self.page.locator("#optionsSelectDay").select_option(label=day_str)
        self.page.wait_for_timeout(100)
        self.page.locator("#optionsSelectYear").select_option(label=str(dob.year))
        self.page.wait_for_timeout(200)

    def select_sex(self) -> None:
        """Randomly select one of the available sex options."""
        sex_buttons = [
            "#rb_sex_female",
            "#rb_sex_male",
            "#rb_sex_other",
            "#rb_sex_declinetostate",
        ]
        chosen = random.choice(sex_buttons)
        self.page.locator(chosen).click()
        self.page.wait_for_timeout(200)

    def fill_ssn_last4(self, ssn: str) -> None:
        """Fill the SSN last-4 input field."""
        self.page.locator("#id_ssn4").fill(ssn)
        self.page.wait_for_timeout(200)

    def select_party(self) -> None:
        """Randomly select one of the available political party options."""
        party_buttons = [
            "#rb_party_Democratic",
            "#rb_party_Republican",
            "#rb_party_independent",
            "#rb_party_none",
            "#rb_party_declinetostate",
        ]
        chosen = random.choice(party_buttons)
        self.page.locator(chosen).click()
        self.page.wait_for_timeout(200)

    def select_dems_abroad(self) -> None:
        """Answer 'No' to the Join Democrats Abroad question."""
        outreach_no = self.page.locator("#rb_Outreach_no")
        if outreach_no.count() > 0 and outreach_no.is_visible():
            outreach_no.click()
            self.page.wait_for_timeout(200)

    def click_next(self) -> None:
        """Click the Next button and verify navigation to the Sign & Submit step."""
        self.click_next_button()
        self.wait_for_url_contains("/request/sign-submit-nextsteps")
