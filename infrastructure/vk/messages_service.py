from random import randrange
from typing import Any

class MessagesService:
    def __init__(self, vk):
        self.vk = vk

    def _send(self, user_id: int, **params: Any) -> None:
        payload = {
            "user_id": user_id,
            "random_id": randrange(10**7),
            **params,
        }

        self.vk.messages.send(**payload)

    def send_text(self, user_id: int, message: str) -> None:
        self._send(
            user_id=user_id,
            message=message,
        )

    def send_text_with_keyboard(
        self,
        user_id: int,
        message: str,
        keyboard: str,
    ) -> None:
        self._send(
            user_id=user_id,
            message=message,
            keyboard=keyboard,
        )

    def send_attachment(self, user_id: int, attachment: str) -> None:
        self._send(
            user_id=user_id,
            attachment=attachment,
        )

    def send_attachments(self, user_id: int, attachments: list[str]) -> None:
        for attachment in attachments:
            self.send_attachment(
                user_id=user_id,
                attachment=attachment,
            )

    def send_text_attachments_keyboard(
            self,
            user_id: int,
            message: str,
            attachments: list[str],
            keyboard: str | None = None
    ) -> None:
        params = {
            "message": message
        }

        if attachments:
            params["attachment"] = ",".join(attachments)
        
        if keyboard is not None:
            params["keyboard"] = keyboard

        self._send(
            user_id=user_id,
            **params
        )