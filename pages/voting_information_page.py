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
        """Fill the US voting address fields: street, city, state dropdown, zip code, county."""
        self.page.wait_for_timeout(500)  # Wait for Step 2 to fully render
        self.page.locator("#id_votAdr_A").fill(us_address.street)
        self.page.locator("#id_votAdr_C").fill(us_address.city)
        self.page.locator("#id_select_states").select_option(value=us_address.state)
        self.page.locator("#id_votAdr_Z").fill(us_address.zip_code)
        # County field is required for some voter categories
        county_field = self.page.locator("#id_votAdr_Y")
        if county_field.count() > 0 and county_field.is_visible():
            county_field.fill(us_address.city + " County")
        self.page.wait_for_timeout(500)

    def select_jurisdiction(self) -> None:
        """Select the first available voting jurisdiction from the dropdown.

        The jurisdiction field is a typeahead input that shows a list of
        county/borough election offices when clicked. We select the first
        real jurisdiction entry (skipping headers).
        """
        jurisdiction = self.page.locator("#id_jurisdiction")
        if jurisdiction.count() > 0 and jurisdiction.is_visible():
            jurisdiction.click()
            self.page.wait_for_timeout(1000)
            # Find visible <li> items that are actual jurisdictions (skip headers).
            county_items = self.page.locator('li:visible').filter(has_text="Election")
            if county_items.count() > 0:
                county_items.first.click()
                self.page.wait_for_timeout(500)
            else:
                # Fallback: click the second visible li (skip the header)
                all_items = self.page.locator('li:visible')
                if all_items.count() > 1:
                    all_items.nth(1).click()
                    self.page.wait_for_timeout(500)
                else:
                    # Close the dropdown by pressing Escape
                    jurisdiction.press("Escape")
                    self.page.wait_for_timeout(300)
            # Close any remaining dropdown overlay
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)

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
        # Scroll the voter class container into view first — this also closes
        # any jurisdiction dropdown that might be overlaying these buttons
        voter_div = self.page.locator("#id_voterClass")
        voter_div.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
        btn = self.page.locator(chosen)
        btn.click()
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
        """Click the Next button and verify navigation to the ID and Contact step.

        Uses the specific Step 2 Next button ID for reliability, and retries
        if the page doesn't navigate (form validation may block the first click
        if Vue's reactive state hasn't fully committed jurisdiction selection).
        """
        next_btn = self.page.locator("#id_pages_request_stage_next_02")
        next_btn.scroll_into_view_if_needed()
        next_btn.click()
        try:
            self.wait_for_url_contains("/request/id-and-contact-information")
        except Exception:
            # Re-select jurisdiction in case it was cleared by Vue reactivity,
            # then retry the Next click
            self.page.wait_for_timeout(500)
            self.select_jurisdiction()
            self.page.wait_for_timeout(500)
            next_btn.scroll_into_view_if_needed()
            next_btn.click()
            self.wait_for_url_contains("/request/id-and-contact-information")
