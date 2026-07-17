"""End-to-end happy path test for the FPCA form submission."""

import pytest
from playwright.sync_api import Page

from data.db_verify import DatabaseVerifier
from data.email_verify import EmailVerifier
from data.generator import DataGenerator
from pages.confirmation_page import ConfirmationPage
from pages.home_page import HomePage
from pages.id_contact_page import IdContactPage
from pages.review_page import ReviewPage
from pages.sign_submit_page import SignSubmitPage
from pages.voting_information_page import VotingInformationPage
from pages.your_information_page import YourInformationPage


@pytest.mark.e2e
def test_fpca_happy_path(page) -> None:
    """Complete FPCA form submission with randomly generated data."""
    data = DataGenerator().generate_applicant_data()

    # Create a Mailslurp inbox for this test run
    email_verifier = EmailVerifier()
    mailslurp_email = email_verifier.create_inbox()
    # Override the generated email with the Mailslurp inbox address
    data.email = mailslurp_email

    # Navigate to homepage and dismiss cookie banner
    home = HomePage(page)
    home.navigate()
    home.dismiss_cookie_banner()
    home.click_request_ballot()

    # Step 1: Your Information
    your_info = YourInformationPage(page)
    your_info.fill_title(data.name.title)
    your_info.fill_name(data.name)
    your_info.fill_suffix(data.name.suffix)
    your_info.select_no_previous_name()
    your_info.fill_phone(data.phone)
    your_info.fill_email(data.email)
    your_info.fill_address_abroad(data.abroad_address)
    your_info.click_next()

    # Step 2: Voting Information
    voting_info = VotingInformationPage(page)
    voting_info.fill_us_address(data.us_address)
    voting_info.select_voter_registration()
    voting_info.select_voter_category()
    voting_info.select_ballot_delivery()
    voting_info.select_jurisdiction()
    # Re-assert voter registration after jurisdiction (dropdown can reset it)
    voting_info.select_voter_registration()
    voting_info.click_next()

    # Step 3: ID and Contact Information
    id_contact = IdContactPage(page)
    id_contact.fill_dob(data.dob)
    id_contact.select_sex()
    id_contact.fill_ssn_last4(data.ssn_last4)
    id_contact.select_party()
    id_contact.select_dems_abroad()
    id_contact.click_next()

    # Step 4: Review
    review = ReviewPage(page)
    review.verify_summary_displayed()
    review.click_next()

    # Step 5: Sign & Submit
    sign_submit = SignSubmitPage(page)
    sign_submit.skip_signature()
    sign_submit.select_email_delivery()
    sign_submit.click_next()
    sign_submit.click_send_email()

    # Verify successful completion
    confirmation = ConfirmationPage(page)
    confirmation.verify_success()

    # Step 6: Database Verification
    db = DatabaseVerifier()
    try:
        db.connect()
        record = db.find_record_by_firstname(data.name.first_name, timeout=30)
        assert record is not None, (
            f"Record not found in database for firstname '{data.name.first_name}'"
        )
        db.verify_fields(record, data)
    finally:
        db.close()

    # Step 7: Email Delivery Verification
    try:
        result = email_verifier.verify_email_received()
        print(f"Email received: subject='{result['subject']}', "
              f"from='{result['from']}', text_length={result['text_length']}")
    finally:
        email_verifier.close()
