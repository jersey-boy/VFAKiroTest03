"""Email verification module using Testmail.app.

Creates unique email addresses per test run using the Testmail namespace/tag
system, and verifies that the VFA form submission triggers email delivery.

Email format: {namespace}.{tag}@inbox.testmail.app
"""

import os
import random
import string
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


class EmailVerifier:
    """Creates Testmail.app addresses and verifies email delivery."""

    API_URL = "https://api.testmail.app/api/json"

    def __init__(self, env_path: str = "databaseconnect.env") -> None:
        env_file = Path(env_path)
        if not env_file.exists():
            raise FileNotFoundError(f"{env_path} not found")
        load_dotenv(env_file)

        self.api_key = os.environ.get("TESTMAIL_APIKEY")
        self.namespace = os.environ.get("TESTMAIL_NAMESPACE")
        if not self.api_key:
            raise ValueError("TESTMAIL_APIKEY not found in databaseconnect.env")
        if not self.namespace:
            raise ValueError("TESTMAIL_NAMESPACE not found in databaseconnect.env")

        self.tag = None
        self.email_address = None
        self.start_timestamp = None

    def create_inbox(self) -> str:
        """Generate a unique email address for this test run.

        Returns:
            The email address (e.g., namespace.abc123xyz@inbox.testmail.app).
        """
        # Generate a unique tag for this test run
        self.tag = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        self.email_address = f"{self.namespace}.{self.tag}@inbox.testmail.app"
        self.start_timestamp = int(time.time() * 1000)
        return self.email_address

    def wait_for_email(self, timeout: int = 120) -> dict:
        """Wait for an email to arrive at the test inbox.

        Uses Testmail's livequery feature which holds the connection open
        until an email arrives (with 60s redirect cycles).

        Args:
            timeout: Maximum seconds to wait for the email.

        Returns:
            The email object from the API response.

        Raises:
            TimeoutError: If no email arrives within the timeout.
        """
        if not self.tag:
            raise RuntimeError("No inbox created. Call create_inbox() first.")

        params = {
            "apikey": self.api_key,
            "namespace": self.namespace,
            "tag": self.tag,
            "timestamp_from": self.start_timestamp,
            "livequery": "true",
        }

        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                response = requests.get(
                    self.API_URL,
                    params=params,
                    timeout=65,  # Slightly longer than Testmail's 60s redirect cycle
                    allow_redirects=True,
                )
                data = response.json()

                if data.get("result") == "success" and data.get("count", 0) > 0:
                    return data["emails"][0]

            except requests.exceptions.Timeout:
                # Testmail's livequery timed out, retry if within deadline
                continue
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Testmail API error: {e}") from e

        raise TimeoutError(
            f"No email received within {timeout}s for {self.email_address}"
        )

    def verify_email_received(self, expected_name: str = None) -> dict:
        """Wait for email and verify it was delivered with expected content.

        Args:
            expected_name: If provided, asserts this name appears in the email.

        Returns:
            A dict with email details: subject, from, text preview.

        Raises:
            AssertionError: If the email doesn't contain expected content.
            TimeoutError: If no email arrives.
        """
        email = self.wait_for_email()

        result = {
            "subject": email.get("subject", ""),
            "from": email.get("from", ""),
            "to": email.get("to", ""),
            "text_length": len(email.get("text", "")),
            "text_preview": email.get("text", "")[:200],
            "tag": email.get("tag", ""),
        }

        if expected_name:
            text = email.get("text", "") + email.get("html", "")
            if expected_name.lower() not in text.lower():
                raise AssertionError(
                    f"Expected name '{expected_name}' not found in email. "
                    f"Subject: '{result['subject']}', "
                    f"Text preview: '{result['text_preview']}'"
                )

        return result

    def close(self) -> None:
        """No-op for API compatibility. Testmail doesn't need cleanup."""
        pass
