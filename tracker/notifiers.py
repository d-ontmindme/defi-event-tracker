"""Notification helpers for sending alerts via Twilio and Telegram."""

from __future__ import annotations

import urllib.parse
import urllib.request
from typing import Optional


class AlertManager:
    """Send alerts via Twilio SMS/email and Telegram."""

    def __init__(self,
                 twilio_sid: Optional[str] = None,
                 twilio_token: Optional[str] = None,
                 twilio_from: Optional[str] = None,
                 telegram_token: Optional[str] = None,
                 telegram_chat_id: Optional[str] = None,
                 email_service_sid: Optional[str] = None):
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_from = twilio_from
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.email_service_sid = email_service_sid

    def _twilio_client(self):
        if not (self.twilio_sid and self.twilio_token):
            return None
        try:
            from twilio.rest import Client  # type: ignore
        except Exception:
            return None
        return Client(self.twilio_sid, self.twilio_token)

    def send_sms(self, to_number: str, message: str) -> None:
        client = self._twilio_client()
        if not client or not self.twilio_from:
            return
        client.messages.create(body=message, from_=self.twilio_from, to=to_number)

    def send_email(self, to_email: str, subject: str, message: str) -> None:
        client = self._twilio_client()
        if not client or not self.email_service_sid:
            return
        client.messages.create(
            messaging_service_sid=self.email_service_sid,
            to=to_email,
            subject=subject,
            body=message,
        )

    def send_telegram(self, message: str) -> None:
        if not (self.telegram_token and self.telegram_chat_id):
            return
        payload = urllib.parse.urlencode({"chat_id": self.telegram_chat_id, "text": message}).encode()
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        try:
            urllib.request.urlopen(url, data=payload)
        except Exception:
            pass

