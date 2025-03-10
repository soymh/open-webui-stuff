"""
title: Memory Enhancement Tool for LLM Web UI
author: https://github.com/mhioi
version: 0.0.1
license: MIT
"""

import json
from typing import Callable, Any

from open_webui.apps.webui.models.memories import Memories
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
        USE_MEMORY: bool = Field(
            default=True, description="Enable or disable memory usage."
        )
        DEBUG: bool = Field(default=True, description="Enable or disable debug mode.")

    def __init__(self):
        self.valves = self.Valves()

    async def recall_memories(
        self, __user__: dict, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Retrieves all stored memories from the user's memory vault and provide them to the user for giving the best response. Be accurate and precise. Do not add any additional information. Always use the function to access memory or memories. If the user asks about what is currently stored, only return the exact details from the function. Do not invent or omit any information.

        :return: A numeric list of all memories. You MUST present the memorys to the user as text. It is important that all memorys are displayed without omissions. Please show each memory entry in full!
        """
        emitter = EventEmitter(__event_emitter__)

        user_id = __user__.get("id")

        if not user_id:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        await emitter.emit(
            description="Retrieving stored memories.",
            status="recall_in_progress",
            done=False,
        )

        user_memories = Memories.get_memories_by_user_id(user_id)

        if not user_memories:
            message = "No memory stored."
            await emitter.emit(description=message, status="recall_complete", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        content_list = [
            f"{index}. {memory.content}"
            for index, memory in enumerate(
                sorted(user_memories, key=lambda m: m.created_at), start=1
            )
        ]

        await emitter.emit(
            description=f"{len(user_memories)} memories loaded",
            status="recall_complete",
            done=True,
        )

        return f"Memories from the users memory vault: {content_list}"

    async def add_memory(
        self,
        input_text: str,
        __user__: dict,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Add a new entry to the user's memory vault. Always use the function to actually store the data; do not simulate or pretend to save data without using the function. After adding the entry, retrieve all stored memories from the user's memory vault and provide them accurately. Do not invent or omit any information; only return the data obtained from the function. Do not assume that any input text already exists in the user's memories unless the function explicitly confirms that a duplicate entry is being added. Simply acknowledge the new entry without referencing prior content unless it is confirmed by the memory function.
        - User's name: "xyz"
        - User's age: "30"
        - User's profession: "programmer specializing in Python""


        :params input_text: The TEXT .
        :returns: A numeric list of all memories.
        """
        emitter = EventEmitter(__event_emitter__)
        user_id = __user__.get("id")

        if not user_id:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        await emitter.emit(
            description="Adding entry to the memory vault.",
            status="add_in_progress",
            done=False,
        )

        new_memory = Memories.insert_new_memory(user_id, input_text)

        if not new_memory:
            message = "Failed to add memory."
            await emitter.emit(description=message, status="add_failed", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        # Fetch updated memories after addition
        user_memories = Memories.get_memories_by_user_id(user_id)

        content_list = [
            f"{index}. {memory.content}"
            for index, memory in enumerate(
                sorted(user_memories, key=lambda m: m.created_at), start=1
            )
        ]

        await emitter.emit(
            description=f"Added entry to the memory vault: {content_list}",
            status="add_complete",
            done=True,
        )

        return f"Added to the users memory vault; new memories are: {content_list}"
