"""
title: Discord Webhook
author: mhio
author_url: https://github.com/soymh
version: 0.0.1
"""

import asyncio

import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field


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
        pass

    async def send_message(self, message_content: str) -> str:
        """
        Send a message to a specified Discord channel using a webhook.If user asks or talks about sending a message to the channel in discord,utilize this.

        :param message_content: The content of the message to be sent to the Discord channel.
        :param proxy: Optional proxy URL in the format 'http://username:password@proxyserver:port'.
        :return: Response message indicating success or failure.
        """

        # Check if the webhook URL has been set
        if not self.valves.WEBHOOK_URL:
            await emitter.emit(
                description="No webhook URL, Please configure the webhook URL.",
                status="no_webhook_url",
                done=True,
            )
            return "Let the user know webhook URL was not provided. Please configure the webhook URL."

        data = {"content": f"{message_content} - Sent from Open WebUI"}

        proxies = (
            {"http": self.valves.PROXY, "https": self.valves.PROXY}
            if self.valves.PROXY
            else None
        )

        try:
            response = requests.post(
                self.valves.WEBHOOK_URL, json=data, proxies=proxies
            )

            if response.status_code == 204:
                await emitter.emit(
                    description="Message successfully sent.", status="sent", done=True
                )
                return f"Message{data} successfully sent to the discord channel. Let the user know the message has been sent."
            else:
                await emitter.emit(
                    description="Sending message was unsuccessful.",
                    status="not_sent",
                    done=True,
                )
                return f"Failed to send message. HTTP Status Code: {response.status_code}. Let the user know there were some issues."

        except requests.exceptions.RequestException as e:
            await emitter.emit(
                description=f"Error occurred: {e}",
                status="error",
                done=True,
            )
            return f"Failed to send message:{data} to the specified discord channel, due to the exception: {e}"
