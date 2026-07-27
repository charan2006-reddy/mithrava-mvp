"""SMS provider abstraction for OTP delivery.

Supports multiple providers via a pluggable interface:
- Twilio (international, pay-per-SMS)
- MSG91 (India-focused, cheap/free tier)
- Console (dev/demo — prints to stdout)

Configure via SMS_PROVIDER env var:
  - "twilio"    → TwilioIntegration
  - "msg91"     → MSG91Integration
  - "console"   → ConsoleProvider (default for dev)
  - "" or unset → ConsoleProvider
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("mithrava.sms")


class SMSProvider(ABC):
    """Abstract base class for SMS providers."""

    @abstractmethod
    async def send_otp(self, phone: str, code: str) -> bool:
        """Send an OTP code via SMS.

        Args:
            phone: Recipient phone number (E.164 format).
            code: The 6-digit OTP code.

        Returns:
            True if sent successfully, False otherwise.
        """
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider has all required credentials."""
        ...


class ConsoleProvider(SMSProvider):
    """Dev/demo provider that prints OTP to console.

    Used when no SMS provider is configured, or in development mode.
    """

    def is_configured(self) -> bool:
        return True

    async def send_otp(self, phone: str, code: str) -> bool:
        """Print OTP to console (dev mode)."""
        logger.info("📱 [DEV SMS] OTP for %s: %s", phone, code)
        print(f"\n{'='*50}")
        print(f"  📱 SMS to {phone}")
        print(f"  OTP Code: {code}")
        print(f"{'='*50}\n")
        return True


class TwilioProvider(SMSProvider):
    """Twilio SMS provider.

    Requires:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_FROM_NUMBER (E.164 format, e.g., +1234567890)
    """

    def __init__(self):
        self._account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self._auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self._from_number = os.environ.get("TWILIO_FROM_NUMBER", "")

    def is_configured(self) -> bool:
        return bool(self._account_sid and self._auth_token and self._from_number)

    async def send_otp(self, phone: str, code: str) -> bool:
        """Send OTP via Twilio SMS."""
        if not self.is_configured():
            logger.error("Twilio not configured — missing credentials")
            return False

        try:
            from twilio.rest import Client

            client = Client(self._account_sid, self._auth_token)
            message = client.messages.create(
                body=f"Your Mithrava OTP is: {code}. Valid for 5 minutes. Do not share this code.",
                from_=self._from_number,
                to=phone,
            )
            logger.info("Twilio SMS sent to %s, SID: %s", phone, message.sid)
            return True

        except ImportError:
            logger.error("twilio package not installed. Run: pip install twilio")
            return False
        except Exception as exc:
            logger.error("Twilio SMS failed for %s: %s", phone, exc)
            return False


class MSG91Provider(SMSProvider):
    """MSG91 SMS provider (India-focused, affordable).

    Requires:
      - MSG91_AUTH_KEY
      - MSG91_TEMPLATE_ID (OTP template)
      - MSG91_SENDER_ID (e.g., "MITHRA")

    API docs: https://docs.msg91.com/
    """

    def __init__(self):
        self._auth_key = os.environ.get("MSG91_AUTH_KEY", "")
        self._template_id = os.environ.get("MSG91_TEMPLATE_ID", "")
        self._sender_id = os.environ.get("MSG91_SENDER_ID", "MITHRA")

    def is_configured(self) -> bool:
        return bool(self._auth_key and self._template_id)

    async def send_otp(self, phone: str, code: str) -> bool:
        """Send OTP via MSG91 SMS."""
        if not self.is_configured():
            logger.error("MSG91 not configured — missing credentials")
            return False

        try:
            import httpx

            # Strip leading '+' and country code for MSG91 (expects 10-digit Indian number)
            clean_phone = phone.lstrip("+")
            if clean_phone.startswith("91") and len(clean_phone) > 10:
                clean_phone = clean_phone[2:]

            payload = {
                "route": "4",
                "sender": self._sender_id,
                "sms": [
                    {
                        "message": f"Your Mithrava OTP is {code}. Valid for 5 minutes. Do not share.",
                        "to": [clean_phone],
                    }
                ],
            }

            headers = {
                "authkey": self._auth_key,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.msg91.com/api/v2/sms",
                    json=payload,
                    headers=headers,
                    timeout=10.0,
                )

            if resp.status_code == 200:
                logger.info("MSG91 SMS sent to %s", phone)
                return True
            else:
                logger.error("MSG91 API error %s: %s", resp.status_code, resp.text)
                return False

        except ImportError:
            logger.error("httpx package not installed")
            return False
        except Exception as exc:
            logger.error("MSG91 SMS failed for %s: %s", phone, exc)
            return False


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------


def get_sms_provider() -> SMSProvider:
    """Get the configured SMS provider.

    Reads SMS_PROVIDER env var and returns the appropriate provider.
    Falls back to ConsoleProvider for development.

    Returns:
        Configured SMSProvider instance.
    """
    provider_name = os.environ.get("SMS_PROVIDER", "").lower().strip()

    providers = {
        "twilio": TwilioProvider,
        "msg91": MSG91Provider,
        "console": ConsoleProvider,
    }

    if provider_name in providers:
        provider = providers[provider_name]()
        if provider.is_configured():
            logger.info("Using SMS provider: %s", provider_name)
            return provider
        else:
            logger.warning(
                "SMS provider '%s' is not fully configured — falling back to console",
                provider_name,
            )

    # Default: console (dev mode)
    logger.info("Using console SMS provider (development mode)")
    return ConsoleProvider()
