"""YourInformationPage page object for the Your Information form step."""

from playwright.sync_api import Page

from data.generator import AbroadAddress, NameData
from pages.base_page import BasePage


class YourInformationPage(BasePage):
    """Page object for the 'Your Information' step of the FPCA form."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def fill_title(self, title: str) -> None:
        """Click the title button matching the given title text (e.g., 'Mr.', 'Ms.')."""
        self.page.get_by_role("button", name=title).click()
        self.page.wait_for_timeout(200)

    def fill_name(self, name_data: NameData) -> None:
        """Fill first name, middle name, and last name fields."""
        self.page.locator("#id_firstName").fill(name_data.first_name)
        self.page.locator("#id_middleName").fill(name_data.middle_name)
        self.page.locator("#id_lastName").fill(name_data.last_name)

    def fill_suffix(self, suffix: str) -> None:
        """Click the suffix span matching the given text (e.g., 'Jr.', 'Sr.')."""
        self.page.get_by_role("button", name=suffix, exact=True).click()
        self.page.wait_for_timeout(200)

    def select_no_previous_name(self) -> None:
        """Click the 'No' button for previous name change question."""
        self.page.locator("#rb_previousName_no").click()
        self.page.wait_for_timeout(200)

    def fill_phone(self, phone: str) -> None:
        """Fill the phone number input field."""
        self.page.locator("#vfaititel").fill(phone)
        self.page.wait_for_timeout(200)

    def fill_email(self, email: str) -> None:
        """Fill the email input and click the verify button."""
        self.page.locator('input[type="email"]').fill(email)
        self.page.locator("#rb_emailAddressVerified_true").click()
        self.page.wait_for_timeout(300)

    def fill_address_abroad(self, abroad_address: AbroadAddress) -> None:
        """Fill the abroad address section: country typeahead, address, city, postal code.

        Uses Canada as the country (consistent field structure with City, State, Postal Code).
        """
        # Fill country typeahead
        country_input = self.page.locator('input[placeholder*="type to find your country"]')
        country_input.fill(abroad_address.country)
        # Wait for Vue to re-render the address fields
        self.page.wait_for_timeout(500)

        # Fill address fields using fill()
        self.page.locator("#id_abrAdr_A").fill(abroad_address.address_line1)
        self.page.locator("#id_abrAdr_C").fill(abroad_address.city)

        # State/province — only fill if present (depends on country)
        state_field = self.page.locator("#id_abrAdr_S")
        if state_field.count() > 0 and state_field.is_visible():
            state_field.fill(abroad_address.state_province)

        # Postal code
        zip_field = self.page.locator("#id_abrAdr_Z")
        if zip_field.count() > 0 and zip_field.is_visible():
            zip_field.fill(abroad_address.zip_code)

        self.page.wait_for_timeout(300)

    def click_next(self) -> None:
        """Click the Next button and verify navigation to the Voting Information step."""
        self.click_next_button()
        self.wait_for_url_contains("/request/voting-information")
