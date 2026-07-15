"""Database verification module for FPCA form submissions.

Connects to the PostgreSQL database on AWS RDS and verifies that
submitted form data was persisted correctly.
"""

import os
import time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from data.generator import ApplicantData


class DatabaseVerifier:
    """Verifies form data was written to the PostgreSQL database."""

    TABLE_NAME = "vfa_fpca_form"

    def __init__(self, env_path: str = "databaseconnect.env") -> None:
        env_file = Path(env_path)
        if not env_file.exists():
            raise FileNotFoundError(f"{env_path} not found")
        load_dotenv(env_file)

        self.host = os.environ["DB_HOST"]
        self.port = os.environ.get("DB_PORT", "5432")
        self.dbname = os.environ["DB_NAME"]
        self.user = os.environ["DB_USER"]
        self.password = os.environ["DB_PASSWORD"]
        self.conn = None

    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                connect_timeout=10,
            )
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Cannot connect to database: {e}") from e

    def find_record_by_firstname(
        self, firstname: str, timeout: int = 30
    ) -> dict | None:
        """Poll the database for a record matching the given firstname.

        Args:
            firstname: The unique first name (with random suffix) to search for.
            timeout: Maximum seconds to wait for the record to appear.

        Returns:
            A dict of column names to values if found, None if timeout reached.
        """
        if not self.conn:
            raise RuntimeError("Not connected. Call connect() first.")

        query = """
            SELECT firstname, lastname, email, dob
            FROM vfa_fpca_form
            WHERE firstname = %s
            ORDER BY createdat DESC
            LIMIT 1
        """

        deadline = time.time() + timeout
        while time.time() < deadline:
            with self.conn.cursor() as cur:
                cur.execute(query, (firstname,))
                row = cur.fetchone()
                if row:
                    columns = [desc[0] for desc in cur.description]
                    return dict(zip(columns, row))
            time.sleep(2)

        return None

    def verify_fields(self, record: dict, expected: ApplicantData) -> None:
        """Assert that database fields match the expected applicant data.

        Checks: firstname, lastname, email, dob.
        """
        errors = []

        if record["firstname"] != expected.name.first_name:
            errors.append(
                f"firstname: expected '{expected.name.first_name}' "
                f"got '{record['firstname']}'"
            )

        if record["lastname"] != expected.name.last_name:
            errors.append(
                f"lastname: expected '{expected.name.last_name}' "
                f"got '{record['lastname']}'"
            )

        if record["email"] != expected.email:
            errors.append(
                f"email: expected '{expected.email}' "
                f"got '{record['email']}'"
            )

        # DOB comparison — database may store as date or string
        expected_dob_str = (
            f"{expected.dob.year}-"
            f"{list(['January','February','March','April','May','June','July','August','September','October','November','December']).index(expected.dob.month)+1:02d}-"
            f"{expected.dob.day:02d}"
        )
        db_dob = str(record["dob"])
        if expected_dob_str not in db_dob and db_dob not in expected_dob_str:
            errors.append(
                f"dob: expected '{expected_dob_str}' got '{db_dob}'"
            )

        if errors:
            raise AssertionError(
                "Database field mismatches:\n  " + "\n  ".join(errors)
            )

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
