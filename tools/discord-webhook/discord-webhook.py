"""
title: Discord Webhook
author: https://github.com/soymh
version: 0.0.1
"""

import asyncio
import requests
from pydantic import BaseModel, Field
from typing import Callable, Any


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
        WEBHOOK_URL: str = Field(
            default="",
            description="The URL of the Discord webhook to send messages to.",
        )
        PROXY: str = Field(
            default="",
            description="The proxy used to send the message through.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def send_message(self, message_content: str, __event_emitter__: Callable[[dict], Any] = None) -> str:
        """
        Send a message to a specified Discord channel using a webhook.

        :param message_content: The content of the message to be sent to the Discord channel.
        :param __event_emitter__: An optional callback for emitting events during processing.
        :return: Response message indicating success or failure.
        """
        emitter = EventEmitter(__event_emitter__)

        # Check if the webhook URL has been set
        if not self.valves.WEBHOOK_URL:
            await emitter.emit(description="No webhook URL, Please configure the webhook URL.", status="no_webhook_url", done=True)
            return "Let the user know webhook URL was not provided. Please configure the webhook URL."

        # Emitting event that message sending is in progress
        await emitter.emit(description="Sending message to Discord channel.", status="sending_message", done=False)

        data = {"content": f"{message_content} - Sent from Open WebUI"}

        proxies = (
            {"http": self.valves.PROXY, "https": self.valves.PROXY}
            if self.valves.PROXY
            else None
        )

        try:
            response = requests.post(self.valves.WEBHOOK_URL, json=data, proxies=proxies)

            if response.status_code == 204:
                # Emitting event after successfully sending the message
                await emitter.emit(description="Message successfully sent.", status="message_sent", done=True)
                return f"Message successfully sent to the Discord channel."

            else:
                # Emitting event in case of failure
                await emitter.emit(description="Sending message was unsuccessful.", status="not_sent", done=True)
                return f"Failed to send message. HTTP Status Code: {response.status_code}. Let the user know there were some issues."

        except requests.exceptions.RequestException as e:
            # Emitting event when an exception occurs
            await emitter.emit(description=f"Error occurred: {e}", status="error", done=True)
            return f"Failed to send message to the specified discord channel, due to the exception: {e}"
