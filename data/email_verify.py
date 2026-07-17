"""Email verification module using Mailslurp.

Creates disposable inboxes for each test run and verifies that the VFA
form submission triggers an email delivery to the provided address.
"""

import os
from pathlib import Path

import mailslurp_client
from dotenv import load_dotenv


class EmailVerifier:
    """Creates Mailslurp inboxes and verifies email delivery."""

    def __init__(self, env_path: str = "databaseconnect.env") -> None:
        env_file = Path(env_path)
        if not env_file.exists():
            raise FileNotFoundError(f"{env_path} not found")
        load_dotenv(env_file)

        api_key = os.environ.get("MAILSLURP_API_KEY")
        if not api_key:
            raise ValueError(
                "MAILSLURP_API_KEY not found in databaseconnect.env"
            )

        self.configuration = mailslurp_client.Configuration()
        self.configuration.api_key["x-api-key"] = api_key
        self.api_client = None
        self.inbox = None

    def create_inbox(self) -> str:
        """Create a new disposable inbox and return its email address.

        Returns:
            The email address of the newly created inbox (e.g., abc123@mailslurp.net).
        """
        self.api_client = mailslurp_client.ApiClient(self.configuration)
        inbox_controller = mailslurp_client.InboxControllerApi(self.api_client)
        self.inbox = inbox_controller.create_inbox_with_defaults()
        return self.inbox.email_address

    def wait_for_email(self, timeout: int = 120000) -> mailslurp_client.Email:
        """Wait for an email to arrive in the inbox.

        Args:
            timeout: Maximum milliseconds to wait for the email (default 2 minutes).

        Returns:
            The received Email object.

        Raises:
            TimeoutError: If no email arrives within the timeout period.
            RuntimeError: If no inbox was created.
        """
        if not self.inbox or not self.api_client:
            raise RuntimeError("No inbox created. Call create_inbox() first.")

        wait_controller = mailslurp_client.WaitForControllerApi(self.api_client)
        try:
            email = wait_controller.wait_for_latest_email(
                inbox_id=self.inbox.id,
                timeout=timeout,
                unread_only=True,
            )
            return email
        except mailslurp_client.ApiException as e:
            raise TimeoutError(
                f"No email received within {timeout}ms for {self.inbox.email_address}: {e}"
            ) from e

    def verify_email_received(self, expected_name: str = None) -> dict:
        """Wait for email and verify it was delivered with expected content.

        Args:
            expected_name: If provided, asserts this name appears in the email body.

        Returns:
            A dict with email details: subject, from, body_preview.

        Raises:
            AssertionError: If the email doesn't contain expected content.
            TimeoutError: If no email arrives.
        """
        email = self.wait_for_email()

        result = {
            "subject": email.subject or "",
            "from": email.var_from or "",
            "to": str(email.to) if email.to else "",
            "body_length": len(email.body) if email.body else 0,
            "body_preview": (email.body or "")[:200],
        }

        if expected_name and email.body:
            if expected_name.lower() not in email.body.lower():
                raise AssertionError(
                    f"Expected name '{expected_name}' not found in email body. "
                    f"Subject: '{email.subject}', Body preview: '{email.body[:100]}'"
                )

        return result

    def close(self) -> None:
        """Clean up the API client."""
        if self.api_client:
            self.api_client.close()
            self.api_client = None
