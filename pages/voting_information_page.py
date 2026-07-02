"""VotingInformationPage page object for the Voting Information form step."""

import random

from playwright.sync_api import Page

from data.generator import USAddress
from pages.base_page import BasePage


class VotingInformationPage(BasePage):
    """Page object for the 'Voting Information' step of the FPCA form."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def fill_us_address(self, us_address: USAddress) -> None:
        """Fill the US voting address fields: street, city, state dropdown, zip code."""
        self.page.wait_for_timeout(500)  # Wait for Step 2 to fully render
        self.page.locator("#id_votAdr_A").fill(us_address.street)
        self.page.locator("#id_votAdr_C").fill(us_address.city)
        self.page.locator("#id_select_states").select_option(value=us_address.state)
        self.page.locator("#id_votAdr_Z").fill(us_address.zip_code)
        self.page.wait_for_timeout(500)

    def select_jurisdiction(self) -> None:
        """Select the first available voting jurisdiction from the dropdown.

        The jurisdiction field appears after a state is selected and lists
        county election offices for that state.
        """
        jurisdiction = self.page.locator("#id_jurisdiction")
        if jurisdiction.count() > 0 and jurisdiction.is_visible():
            jurisdiction.click()
            self.page.wait_for_timeout(500)
            # Click the first county item in the dropdown list
            county_items = self.page.locator('li:visible').filter(has_text="County")
            if county_items.count() > 0:
                county_items.first.click()
                self.page.wait_for_timeout(300)

    def select_voter_registration(self) -> None:
        """Select 'Yes' for the voter registration question."""
        self.page.locator("#rb_voterRegistration_registered").click()
        self.page.wait_for_timeout(200)

    def select_voter_category(self) -> None:
        """Randomly select one voter category from the available options."""
        voter_class_buttons = [
            "#id_rb_voterClass_intendToReturn",
            "#id_rb_voterClass_uncertainReturn",
            "#id_rb_voterClass_neverResided",
            "#id_rb_voterClass_military",
            "#id_rb_voterClass_milSpouse",
        ]
        chosen = random.choice(voter_class_buttons)
        self.page.evaluate(f"""() => {{
            const btn = document.querySelector('{chosen}');
            btn.scrollIntoView();
            btn.click();
        }}""")
        self.page.wait_for_timeout(300)

    def select_ballot_delivery(self) -> None:
        """Select email as the ballot delivery method.

        This option appears after selecting a voter category.
        """
        delivery_btn = self.page.locator("#rb_recBallot_email")
        if delivery_btn.count() > 0 and delivery_btn.is_visible():
            delivery_btn.click()
            self.page.wait_for_timeout(200)

    def click_next(self) -> None:
        """Click the Next button and verify navigation to the ID and Contact step."""
        self.click_next_button()
        self.wait_for_url_contains("/request/id-and-contact-information")
