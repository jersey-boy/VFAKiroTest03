# Implementation Plan: Playwright Test Suite

## Overview

Implement a single end-to-end Playwright happy-path test for the FPCA ballot request form on VoteFromAbroad. The implementation follows the Page Object Model pattern in Python with pytest-playwright, using Faker for realistic data generation and Hypothesis for property-based testing of the data layer.

## Tasks

- [x] 1. Set up project structure and dependencies
  - [x] 1.1 Create project configuration files
    - Create `requirements.txt` with playwright, pytest, pytest-playwright, hypothesis, and faker dependencies (pinned versions)
    - Create `pytest.ini` with pytest configuration (testpaths, markers)
    - Create `__init__.py` files for `data/`, `pages/`, and `tests/` packages
    - _Requirements: 1.5_

  - [x] 1.2 Create conftest.py with pytest-playwright fixtures
    - Configure browser context args (viewport 1920x1080)
    - Leverage pytest-playwright's built-in `page` fixture for browser lifecycle
    - Headless/headed mode controlled via `--headed` CLI flag
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implement data generation layer
  - [x] 2.1 Create data models
    - Define `NameData`, `DateOfBirth`, `USAddress`, `AbroadAddress`, and `ApplicantData` dataclasses in `data/generator.py`
    - _Requirements: 2.1, 2.4, 2.5_

  - [x] 2.2 Implement DataGenerator class
    - Implement `generate_name()` with random title and suffix selection
    - Implement `generate_phone()` returning 10-digit US phone number
    - Implement `generate_email()` returning valid email format
    - Implement `generate_dob(min_age=18)` ensuring adult age
    - Implement `generate_us_address()` with valid state abbreviation and 5-digit zip
    - Implement `generate_abroad_address()` with non-US country
    - Implement `generate_ssn_last4()` returning exactly 4 digits
    - Implement `generate_applicant_data()` that combines all generators
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 2.3 Write property test for name generation
    - **Property 1: Generated names are always non-empty strings**
    - **Validates: Requirements 2.1**

  - [ ]* 2.4 Write property test for email generation
    - **Property 2: Generated emails are always valid format**
    - **Validates: Requirements 2.2**

  - [ ]* 2.5 Write property test for phone generation
    - **Property 3: Generated phone numbers are always exactly 10 numeric digits**
    - **Validates: Requirements 2.3**

  - [ ]* 2.6 Write property test for date of birth generation
    - **Property 4: Generated dates of birth always represent adults aged 18 or older**
    - **Validates: Requirements 2.4**

  - [ ]* 2.7 Write property test for US address generation
    - **Property 5: Generated US addresses have valid state code and zip format**
    - **Validates: Requirements 2.5**

  - [ ]* 2.8 Write property test for SSN last-4 generation
    - **Property 6: Generated SSN last-4 is always exactly 4 numeric digits**
    - **Validates: Requirements 2.7**

- [x] 3. Checkpoint - Ensure data layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement base page object and HomePage
  - [x] 4.1 Create BasePage class
    - Define `PAGE_TRANSITION_TIMEOUT = 15_000` and `FIELD_INTERACTION_TIMEOUT = 5_000` constants
    - Implement `wait_for_url_contains(path)` using `page.wait_for_url()`
    - Implement `click_next_button()` using the site's Next button locator
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 4.2 Create HomePage page object
    - Implement `navigate()` to go to `https://vfa-newux.netlify.app/`
    - Implement `dismiss_cookie_banner()` — click "Accept All", handle absence gracefully with 5s timeout
    - Implement `click_request_ballot()` — click the landing page button and verify navigation to `/request/your-information`
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

- [x] 5. Implement Step 1 page object — Your Information
  - [x] 5.1 Create YourInformationPage class
    - Implement `fill_title(title)` — click the title button matching the given title text
    - Implement `fill_name(name_data)` — fill first name, middle name, last name fields by ID
    - Implement `fill_suffix(suffix)` — click the suffix span matching text
    - Implement `select_no_previous_name()` — click `#rb_previousName_no`
    - Implement `fill_phone(phone)` — fill the phone input `#vfaititel`
    - Implement `fill_email(email)` — fill email input and click verify button `#rb_emailAddressVerified_true`
    - Implement `fill_address_abroad(abroad_address)` — fill country typeahead, address, city, postal code
    - Implement `click_next()` — click Next and verify URL contains `/request/voting-information`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12_

- [x] 6. Implement Step 2 page object — Voting Information
  - [x] 6.1 Create VotingInformationPage class
    - Implement `fill_us_address(us_address)` — fill street, city, state dropdown, zip code
    - Implement `select_voter_category()` — randomly select from available voter category options
    - Implement `click_next()` — click Next and verify URL contains `/request/id-and-contact-information`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [x] 7. Implement Step 3 page object — ID and Contact Information
  - [x] 7.1 Create IdContactPage class
    - Implement `fill_dob(dob)` — select month, day, year from date of birth dropdowns
    - Implement `select_sex()` — randomly select from available sex options
    - Implement `fill_ssn_last4(ssn)` — fill the SSN last-4 field
    - Implement `select_party()` — randomly select from available political party options
    - Implement `select_dems_abroad()` — randomly select from Democrats Abroad options
    - Implement `click_next()` — click Next and verify URL contains `/request/sign-submit-nextsteps`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [x] 8. Implement Step 4 and Step 5 page objects
  - [x] 8.1 Create ReviewPage class
    - Implement `verify_summary_displayed()` — confirm summary content is visible
    - Implement `click_next()` — click Next to advance to Sign & Submit flow
    - _Requirements: 8.1, 8.2_

  - [x] 8.2 Create SignSubmitPage class
    - Implement `skip_signature()` — select option to not attach signature
    - Implement `select_email_delivery()` — select "Email directly to you" option
    - Implement `click_next()` — click Next on the final review sub-page
    - Implement `click_send_email()` — click "Send email" button and wait for completion
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 8.3 Create ConfirmationPage class
    - Implement `verify_success()` — confirm page contains success/submitted/complete/confirmation text
    - Fail test with descriptive timeout error if confirmation does not appear
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 9. Checkpoint - Ensure page objects compile cleanly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement the E2E happy-path test
  - [x] 10.1 Create test_fpca_happy_path.py
    - Import all page objects and DataGenerator
    - Implement `test_fpca_happy_path(page)` function that:
      - Generates applicant data via `DataGenerator().generate_applicant_data()`
      - Navigates to homepage and dismisses cookie banner
      - Clicks "Request your ballot"
      - Fills Step 1 (Your Information) with generated data
      - Fills Step 2 (Voting Information) with generated data
      - Fills Step 3 (ID and Contact Information) with generated data
      - Advances through Step 4 (Review)
      - Completes Step 5 (Sign & Submit) with no-signature and email delivery
      - Verifies successful completion on the confirmation page
    - _Requirements: 1.1, 1.2, 3.1, 4.1, 4.2, 4.3, 5.11, 5.12, 6.6, 6.7, 7.6, 7.7, 8.1, 8.2, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 11.1, 11.2, 11.3, 11.4_

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate the Data Generator layer using Hypothesis (framework-agnostic, no browser needed)
- The E2E test requires Playwright browsers installed (`playwright install chromium`)
- Run `pip install -r requirements.txt` before executing any tests

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3", "2.4", "2.5", "2.6", "2.7", "2.8"] },
    { "id": 4, "tasks": ["4.1"] },
    { "id": 5, "tasks": ["4.2", "5.1", "6.1", "7.1"] },
    { "id": 6, "tasks": ["8.1", "8.2", "8.3"] },
    { "id": 7, "tasks": ["10.1"] }
  ]
}
```


---

## Database Verification Tasks

- [ ] 12. Add database verification dependencies
  - [ ] 12.1 Add `psycopg2-binary` and `python-dotenv` to `requirements.txt`
    - _Requirements: 12.2, 12.7_

- [ ] 13. Implement first name uniqueness
  - [ ] 13.1 Modify `DataGenerator.generate_name()` to append a 4-character random alphanumeric suffix to the first name
    - _Requirements: 13.1, 13.2, 13.3_

- [ ] 14. Implement database verification module
  - [ ] 14.1 Create `data/db_verify.py` with `DatabaseVerifier` class
    - Implement `__init__()` to load credentials from `databaseconnect.env` using `python-dotenv`
    - Implement `connect()` to establish PostgreSQL connection via `psycopg2`
    - Implement `find_record_by_firstname(firstname, timeout=30)` with polling/retry
    - Implement `verify_fields(record, expected_data)` to assert firstname, lastname, email, dob match
    - Implement `close()` to close the database connection
    - _Requirements: 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

- [ ] 15. Integrate DB verification into the E2E test
  - [ ] 15.1 Update `conftest.py` to load `databaseconnect.env` at session start
    - _Requirements: 12.7_

  - [ ] 15.2 Update `test_fpca_happy_path.py` to call `DatabaseVerifier` after confirmation page verification
    - Connect to DB, find record by unique firstname, verify fields, close connection
    - _Requirements: 12.2, 12.3, 12.4, 12.5, 12.6_

- [ ] 16. Checkpoint — Verify DB integration compiles and test passes
  - Ensure code compiles cleanly and test runs end-to-end including DB verification

