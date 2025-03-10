"""
title: Telegram Bot Message Sender
author: https://github.com/soymh
version: 0.0.1
"""

import requests
import asyncio
from typing import Callable, Any

from pydantic import BaseModel, Field


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def emit(self, description="Unknown state", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )


class Tools:
    class Valves(BaseModel):
        BOT_TOKEN: str = Field(
            default="",
            description="The token of the Telegram bot.",
        )
        CHAT_ID: int = Field(
            default=0,
            description="The chat ID of the user to receive messages.",
        )
        PROXY: str = Field(
            default="",
            description="The proxy used to send the message through.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def send_message(
        self, message_content: str, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Send a message to a specified Telegram user using a bot.

        :param message_content: The content of the message to be sent.
        :param __event_emitter__: An optional callback for emitting events during processing.
        :return: Response message indicating success or failure.
        """
        emitter = EventEmitter(__event_emitter__)

        # Check if the bot token and chat ID have been set
        if not self.valves.BOT_TOKEN or not self.valves.CHAT_ID:
            await emitter.emit(
                description="Bot token or chat ID not provided.",
                status="missing_configuration",
                done=True,
            )
            return "Bot token or chat ID not provided. Please tell the user to configure them."

        # Start emitting status
        await emitter.emit(
            description="Sending message to Telegram user.",
            status="sending_message",
            done=False,
        )

        url = f"https://api.telegram.org/bot{self.valves.BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": self.valves.CHAT_ID,
            "text": message_content,
        }

        # Proxy support (optional)
        proxies = (
            {"http": self.valves.PROXY, "https": self.valves.PROXY}
            if self.valves.PROXY
            else None
        )

        try:
            response = requests.post(url, data=data, proxies=proxies)

            if response.status_code == 200:
                await emitter.emit(
                    description="Message successfully sent.",
                    status="message_sent",
                    done=True,
                )
                return "Message successfully sent to the Telegram user."
            else:
                await emitter.emit(
                    description=f"Failed to send message. HTTP Status Code: {response.status_code}.",
                    status="send_failed",
                    done=True,
                )
                return (
                    f"Failed to send message. HTTP Status Code: {response.status_code}."
                )

        except requests.exceptions.RequestException as e:
            await emitter.emit(
                description=f"Failed to send message due to the exception: {e}",
                status="error",
                done=True,
            )
            return f"Failed to send message due to the exception: {e}"
