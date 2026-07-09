"""Data models and generator for FPCA form test data."""

import random
from dataclasses import dataclass
from typing import Optional

from faker import Faker


@dataclass
class NameData:
    """Applicant name components."""
    title: str        # "Miss", "Ms.", "Mrs.", "Mr."
    first_name: str
    middle_name: str
    last_name: str
    suffix: str       # "Sr.", "Jr.", "II", "III", "IV"


@dataclass
class DateOfBirth:
    """Date of birth components for form dropdowns."""
    month: str        # Full month name (e.g., "January")
    day: int          # 1-31
    year: int         # e.g., 1985


@dataclass
class USAddress:
    """US voting address components."""
    street: str
    city: str
    state: str        # 2-letter abbreviation
    zip_code: str     # 5-digit string


@dataclass
class AbroadAddress:
    """Current address abroad components."""
    country: str      # Country name (not "United States")
    address_line1: str
    city: str
    state_province: str
    zip_code: str


@dataclass
class ApplicantData:
    """Complete applicant data for the FPCA form."""
    name: NameData
    phone: str             # 10-digit US phone number
    email: str             # Valid email format
    dob: DateOfBirth       # Age >= 18
    us_address: USAddress
    abroad_address: AbroadAddress
    ssn_last4: str         # Exactly 4 digits
    voter_category: Optional[str] = None  # Selected at runtime from available options
    sex: Optional[str] = None             # Selected at runtime
    party: Optional[str] = None           # Selected at runtime
    dems_abroad: Optional[str] = None     # Selected at runtime


# Valid US state abbreviations
US_STATE_ABBREVIATIONS = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
]

TITLE_CHOICES = ["Miss", "Ms.", "Mrs.", "Mr."]
SUFFIX_CHOICES = ["Sr.", "Jr.", "II", "III", "IV"]

# Countries known to work with the VFA site's country typeahead component
# Each country has a different address field layout:
#   Canada: Address1, Address2, City, State/Province, Postal Code
#   United Kingdom: Address1, Address2, Address3, City, Postal Code (no State)
#   Germany: Address1, Address2, Postal Code, City (no State, different order)
ABROAD_COUNTRY_CHOICES = [
    "Canada",
    "United Kingdom",
    "Germany",
]


class DataGenerator:
    """Generates realistic randomized test data for FPCA form fields."""

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)

    def generate_name(self) -> NameData:
        """Generate a random applicant name with title and suffix."""
        return NameData(
            title=random.choice(TITLE_CHOICES),
            first_name=self.fake.first_name(),
            middle_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            suffix=random.choice(SUFFIX_CHOICES),
        )

    def generate_phone(self) -> str:
        """Generate a 10-digit US phone number (digits only, no formatting).

        Starts with a valid area code (2-9 for first digit, 0-9 for rest).
        """
        # US phone numbers start with area code (first digit 2-9)
        first_digit = str(random.randint(2, 9))
        rest = self.fake.numerify("#########")
        return first_digit + rest

    def generate_email(self) -> str:
        """Generate a valid email address."""
        return self.fake.email()

    def generate_dob(self, min_age: int = 18) -> DateOfBirth:
        """Generate a date of birth ensuring the person is at least min_age years old."""
        dob = self.fake.date_of_birth(minimum_age=min_age)
        return DateOfBirth(
            month=dob.strftime("%B"),  # Full month name
            day=dob.day,
            year=dob.year,
        )

    def generate_us_address(self) -> USAddress:
        """Generate a US address with a valid state/zip/city combination.

        Uses known-valid combinations to satisfy the VFA site's state-zip validation.
        """
        valid_combos = [
            ("CA", "95014", "Cupertino"),
            ("CA", "90210", "Beverly Hills"),
            ("NY", "10001", "New York"),
            ("TX", "78701", "Austin"),
            ("FL", "33101", "Miami"),
            ("IL", "60601", "Chicago"),
            ("WA", "98101", "Seattle"),
        ]
        state, zip_code, city = random.choice(valid_combos)
        return USAddress(
            street=self.fake.building_number() + " " + self.fake.street_name(),
            city=city,
            state=state,
            zip_code=zip_code,
        )

    def generate_abroad_address(self) -> AbroadAddress:
        """Generate an address abroad with a country that is not United States.

        Each country uses realistic address data appropriate for that country's
        postal format. The state_province field is only used by countries that
        show the State/Province input (e.g., Canada).
        """
        country = random.choice(ABROAD_COUNTRY_CHOICES)

        if country == "Canada":
            return AbroadAddress(
                country=country,
                address_line1=self.fake.building_number() + " " + self.fake.street_name(),
                city="Toronto",
                state_province="ON",
                zip_code="M5V 2T6",
            )
        elif country == "United Kingdom":
            return AbroadAddress(
                country=country,
                address_line1=self.fake.building_number() + " " + self.fake.street_name(),
                city="London",
                state_province="",  # UK doesn't show state field
                zip_code="SW1A 1AA",
            )
        else:  # Germany
            return AbroadAddress(
                country=country,
                address_line1=self.fake.street_name() + " " + self.fake.building_number(),
                city="Berlin",
                state_province="",  # Germany doesn't show state field
                zip_code="10115",
            )

    def generate_ssn_last4(self) -> str:
        """Generate exactly 4 random digits for SSN last-4."""
        return self.fake.numerify("####")

    def generate_applicant_data(self) -> ApplicantData:
        """Generate a complete set of applicant data combining all generators."""
        return ApplicantData(
            name=self.generate_name(),
            phone=self.generate_phone(),
            email=self.generate_email(),
            dob=self.generate_dob(),
            us_address=self.generate_us_address(),
            abroad_address=self.generate_abroad_address(),
            ssn_last4=self.generate_ssn_last4(),
        )
