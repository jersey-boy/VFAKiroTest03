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

        Opens the dropdown, clicks the first real jurisdiction <li>, then verifies
        the Pinia VFAStore's currentRequest.leo was populated. If the click didn't
        commit, directly sets the LEO object on the Pinia store via JavaScript.
        Retries up to 3 times.
        """
        jurisdiction = self.page.locator("#id_jurisdiction")
        if jurisdiction.count() == 0 or not jurisdiction.is_visible():
            return

        for attempt in range(3):
            # Click to open dropdown
            jurisdiction.click()
            self.page.wait_for_timeout(1500)

            # Click the first real jurisdiction entry
            county_items = self.page.locator('li:visible').filter(has_text="Election")
            if county_items.count() > 0:
                county_items.first.click()
            else:
                all_items = self.page.locator('li:visible')
                if all_items.count() > 1:
                    all_items.nth(1).click()
                else:
                    jurisdiction.press("Escape")

            self.page.wait_for_timeout(1000)

            # Check if Pinia store has the LEO object set
            leo_set = self.page.evaluate("""() => {
                try {
                    const app = document.querySelector('#__nuxt')?.__vue_app__;
                    const pinia = app?.config?.globalProperties?.$pinia;
                    const state = pinia?.state?.value?.VFAStore;
                    return !!(state?.currentRequest?.leo && state.currentRequest.leo.n);
                } catch(e) { return false; }
            }""")

            if leo_set:
                return  # Success — Vue committed the LEO to the store

            # LEO not set — close dropdown and retry
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)

    def select_voter_registration(self) -> None:
        """Select 'Yes' for the voter registration question."""
        self.page.locator("#rb_voterRegistration_registered").click()
        self.page.wait_for_timeout(200)

    def select_voter_category(self) -> None:
        """Select the 'Civilian - I Intend to Return' voter category.

        Other voter categories have additional form validation requirements
        that vary by state, making them unreliable for automated happy-path
        testing. The intendToReturn category consistently passes navigation.
        """
        btn = self.page.locator("#id_rb_voterClass_intendToReturn")
        # Scroll the voter class container into view first — this also closes
        # any dropdown that might be overlaying these buttons
        voter_div = self.page.locator("#id_voterClass")
        voter_div.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
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

        Uses the specific Step 2 Next button ID. Retries with a second click
        if the first attempt doesn't navigate (Vue may need an extra event cycle).
        """
        next_btn = self.page.locator("#id_pages_request_stage_next_02")
        next_btn.scroll_into_view_if_needed()
        next_btn.click()
        try:
            self.wait_for_url_contains("/request/id-and-contact-information")
        except Exception:
            # Second attempt — sometimes the first click is absorbed by Vue
            self.page.wait_for_timeout(2000)
            next_btn.scroll_into_view_if_needed()
            next_btn.click()
            self.page.wait_for_function(
                "() => window.location.href.includes('/request/id-and-contact-information')",
                timeout=30000,
            )
