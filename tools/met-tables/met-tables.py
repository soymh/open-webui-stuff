"""
title: Memory Enhancement Tool for LLM Web UI
author: https://github.com/soymh
version: 0.1.0
license: MIT

Thanks to https://github.com/CookSleep,
we added functionalities of update and delete memory
from https://openwebui.com/t/cooksleep/memory,
so that this tool be completed and function the best as it can. 
Huge thanks to https://openwebui.com/t/cooksleep/memory
"""

import json
from typing import Callable, Any, List

from open_webui.models.memories import Memories
from pydantic import BaseModel, Field


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def emit(self, description="Unknown state", status="in_progress", done=False):
        """
        Send a status event to the event emitter.

        :param description: Event description
        :param status: Event status
        :param done: Whether the event is complete
        """
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
        self, __user__: dict = None, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Retrieves all stored memories from the user's memory vault and provide them to the user for giving the best response. Be accurate and precise. Do not add any additional information. Always use the function to access memory or memories. If the user asks about what is currently stored, only return the exact details from the function. Do not invent or omit any information.

        :return: A numeric list of all memories. You MUST present the memorys to the user as text. It is important that all memorys are displayed without omissions. Please show each memory entry in full!
        """
        emitter = EventEmitter(__event_emitter__)

        if not __user__:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

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
        input_text: List[str],
        __user__: dict = None,
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
        if not __user__:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        user_id = __user__.get("id")
        if not user_id:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        if isinstance(input_text, str):
            input_text = [input_text]

        await emitter.emit(
            description="Adding entries to the memory vault.",
            status="add_in_progress",
            done=False,
        )

        added_items = []
        failed_items = []

        for item in input_text:
            new_memory = Memories.insert_new_memory(user_id, item)
            if new_memory:
                added_items.append(item)
            else:
                failed_items.append(item)

        if not added_items:
            message = "Failed to add any memories."
            await emitter.emit(description=message, status="add_failed", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        added_count = len(added_items)
        failed_count = len(failed_items)

        if failed_count > 0:
            message = (
                f"Added {added_count} memories, failed to add {failed_count} memories."
            )
        else:
            message = f"Successfully added {added_count} memories."

        await emitter.emit(
            description=message,
            status="add_complete",
            done=True,
        )
        return json.dumps({"message": message}, ensure_ascii=False)

    async def delete_memory(
        self,
        indices: List[int],
        __user__: dict = None,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Delete one or more memory entries from the user's memory vault.

        Use to remove outdated or incorrect memories.

        For single deletion: provide an integer index
        For multiple deletions: provide a list of integer indices

        Indices refer to the position in the sorted list (1-based).

        :param indices: Single index (int) or list of indices to delete
        :param __user__: User dictionary containing the user ID
        :param __event_emitter__: Optional event emitter
        :return: JSON string with result message
        """
        emitter = EventEmitter(__event_emitter__)

        if not __user__:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        user_id = __user__.get("id")
        if not user_id:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        if isinstance(indices, int):
            indices = [indices]

        await emitter.emit(
            description=f"Deleting {len(indices)} memory entries.",
            status="delete_in_progress",
            done=False,
        )

        user_memories = Memories.get_memories_by_user_id(user_id)
        if not user_memories:
            message = "No memories found to delete."
            await emitter.emit(description=message, status="delete_failed", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        sorted_memories = sorted(user_memories, key=lambda m: m.created_at)
        responses = []

        for index in indices:
            if index < 1 or index > len(sorted_memories):
                message = f"Memory index {index} does not exist."
                responses.append(message)
                await emitter.emit(
                    description=message, status="delete_failed", done=False
                )
                continue

            memory_to_delete = sorted_memories[index - 1]
            result = Memories.delete_memory_by_id(memory_to_delete.id)
            if not result:
                message = f"Failed to delete memory at index {index}."
                responses.append(message)
                await emitter.emit(
                    description=message, status="delete_failed", done=False
                )
            else:
                message = f"Memory at index {index} deleted successfully."
                responses.append(message)
                await emitter.emit(
                    description=message, status="delete_success", done=False
                )

        await emitter.emit(
            description="All requested memory deletions have been processed.",
            status="delete_complete",
            done=True,
        )
        return json.dumps({"message": "\n".join(responses)}, ensure_ascii=False)

    async def update_memory(
        self,
        updates: List[dict],
        __user__: dict = None,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Update one or more memory entries in the user's memory vault.

        Use to modify existing memories when information changes.

        For single update: provide a dict with 'index' and 'content' keys
        For multiple updates: provide a list of dicts with 'index' and 'content' keys

        The 'index' refers to the position in the sorted list (1-based).

        Common scenarios: Correcting information, adding details,
        updating preferences, or refining wording.

        :param updates: Dict with 'index' and 'content' keys OR a list of such dicts
        :param __user__: User dictionary containing the user ID
        :param __event_emitter__: Optional event emitter
        :return: JSON string with result message
        """
        emitter = EventEmitter(__event_emitter__)

        if not __user__:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        user_id = __user__.get("id")
        if not user_id:
            message = "User ID not provided."
            await emitter.emit(description=message, status="missing_user_id", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        await emitter.emit(
            description=f"Updating {len(updates)} memory entries.",
            status="update_in_progress",
            done=False,
        )

        user_memories = Memories.get_memories_by_user_id(user_id)
        if not user_memories:
            message = "No memories found to update."
            await emitter.emit(description=message, status="update_failed", done=True)
            return json.dumps({"message": message}, ensure_ascii=False)

        sorted_memories = sorted(user_memories, key=lambda m: m.created_at)
        responses = []

        for update_item in updates:
            index = update_item.get("index")
            content = update_item.get("content")

            if index < 1 or index > len(sorted_memories):
                message = f"Memory index {index} does not exist."
                responses.append(message)
                await emitter.emit(
                    description=message, status="update_failed", done=False
                )
                continue

            memory_to_update = sorted_memories[index - 1]
            updated_memory = Memories.update_memory_by_id(memory_to_update.id, content)
            if not updated_memory:
                message = f"Failed to update memory at index {index}."
                responses.append(message)
                await emitter.emit(
                    description=message, status="update_failed", done=False
                )
            else:
                message = f"Memory at index {index} updated successfully."
                responses.append(message)
                await emitter.emit(
                    description=message, status="update_success", done=False
                )

        await emitter.emit(
            description="All requested memory updates have been processed.",
            status="update_complete",
            done=True,
        )
        return json.dumps({"message": "\n".join(responses)}, ensure_ascii=False)
