"""
title: Memory Enhancement Tool for LLM Web UI
author: https://github.com/mhioi
version: 1.0.0
license: MIT
"""

import os
import json
from typing import Callable, Any
import asyncio
import datetime
from pydantic import BaseModel, Field


class MemoryFunctions:
    def __init__(self, memory_file="memory.json", debug=False):
        self.memory_file = memory_file
        self.debug = debug
        self.memory_data = self.load_memory()
        self.tag_options = ["personal", "work", "education", "life", "person", "others"]

    def switch_memory_file(self, new_file: str):
        """Switches and initializes operations on a new memory FILE;only do if the user indicates a file process."""
        self.memory_file = new_file
        self.memory_data = self.load_memory()
        if self.debug:
            print(f"Switched to memory file: {self.memory_file}")

    def reindex_memory(self):
        if self.debug:
            print("Reindexing memory entries.")

        # Reindex memory in ascending order
        sorted_indices = sorted(self.memory_data.keys())
        reindexed_memory = {
            new_index + 1: self.memory_data[old_index]
            for new_index, old_index in enumerate(sorted_indices)
        }
        self.memory_data = reindexed_memory
        self.save_memory()

        return "Memory reindexed successfully."

    def delete_memory_by_index(self, index: int):
        if index in self.memory_data:
            del self.memory_data[index]
            self.save_memory()
            return f"Memory index {index} deleted successfully."
        else:
            return f"Memory index {index} does not exist."

    def update_memory_by_index(self, index: int, tag: str, memo: str, by: str):
        if index in self.memory_data:
            if tag not in self.tag_options:
                tag = "others"

            # Update the entry
            self.memory_data[index]["tag"] = tag
            self.memory_data[index]["memo"] = memo
            self.memory_data[index]["by"] = by
            self.memory_data[index]["last_modified"] = datetime.datetime.now().strftime(
                "%Y-%m-%d_%H:%M:%S"
            )
            self.save_memory()
            return f"Memory index {index} updated successfully."
        else:
            return f"Memory index {index} does not exist."

    def load_memory(self):
        if os.path.exists(self.memory_file):
            if self.debug:
                print(f"Loading memory from {self.memory_file}")
            with open(self.memory_file, "r") as file:
                return json.load(file)
        else:
            return {}

    def save_memory(self):
        if self.debug:
            print(f"Saving memory to {self.memory_file}")
        with open(self.memory_file, "w") as file:
            json.dump(self.memory_data, file, ensure_ascii=False, indent=4)

    def add_to_memory(self, tag: str, memo: str, by: str):
        if tag not in self.tag_options:
            tag = "others"

        index = len(self.memory_data) + 1
        entry = {
            "tag": tag,
            "memo": memo,
            "by": by,
            "last_modified": datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        }
        self.memory_data[index] = entry
        self.save_memory()

    # Other methods remain unchanged...
    def retrieve_from_memory(self, key: str):
        if self.debug:
            print(f"Retrieving from memory: {key}")
        return self.memory_data.get(key, None)

    def process_input_for_memory(self, input_text: str):
        return {"timestamp": str(datetime.datetime.now()), "input": input_text}

    def get_all_memories(self) -> dict:
        if self.debug:
            print("Retrieving all memories.")
        return self.memory_data

    def clear_memory(self):
        if self.debug:
            print("Clearing all memory entries.")
        self.memory_data.clear()
        self.save_memory()
        return "ALL MEMORIES CLEARED!"


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
        MEMORY_REFRESH_INTERVAL: int = Field(
            default=60,
            description="Interval in minutes to refresh and analyze memory data.",
        )
        DEBUG: bool = Field(default=True, description="Enable or disable debug mode.")

    def __init__(self):
        self.valves = self.Valves()
        self.memory = MemoryFunctions(debug=self.valves.DEBUG)
        self.confirmation_pending = False

    async def handle_input(
        self,
        input_text: str,
        tag: str,
        user_wants_to_add: bool,
        llm_wants_to_add: bool,
        by: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        AUTOMATICALLY Summarize user input and enhance responses using memory data.

        :params input_text: The TEXT .
        :returns: The response considering memory data.
        """
        emitter = EventEmitter(__event_emitter__)

        if self.valves.DEBUG:
            print(f"Handling input: {input_text}")

        await emitter.emit(f"Analyzing input for memory: {input_text}")

        if self.valves.USE_MEMORY:
            # Assume 'by' is determined outside and 'tag' is selected by LLM
            if tag not in self.memory.tag_options:
                tag = "others"

            if user_wants_to_add:
                await emitter.emit(
                    description=f"User requested to add to memory with tag {tag}",
                    status="memory_update",
                    done=False,
                )
                self.memory.add_to_memory(tag, input_text, "user")
                return "added to memory by user's request!"
            elif llm_wants_to_add:
                await emitter.emit(
                    description=f"LLM added to memory with tag {tag}",
                    status="memory_update",
                    done=False,
                )
                self.memory.add_to_memory(tag, input_text, "LLM")
                return "added to memory by LLM's request!"

        # The remaining logic stays the same.

    async def recall_memories(
        self, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Retrieve all stored memories in current file and provide them to the user.

        :return: A structured representation of all memory contents.
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit(
            "Retrieving all stored memories.", status="recall_in_progress"
        )

        all_memories = self.memory.get_all_memories()
        if not all_memories:
            message = "No memory stored."
            if self.valves.DEBUG:
                print(message)
            await emitter.emit(
                description=message,
                status="recall_complete",
                done=True,
            )
            return json.dumps({"message": message}, ensure_ascii=False)

        # Correctly format stored memories contents for readability
        formatted_memories = json.dumps(all_memories, ensure_ascii=False, indent=4)

        if self.valves.DEBUG:
            print(f"All stored memories retrieved: {formatted_memories}")

        await emitter.emit(
            description=f"All stored memories retrieved: {formatted_memories}",
            status="recall_complete",
            done=True,
        )

        return f"Memories are : {formatted_memories}"

    async def clear_memories(
        self, user_confirmation: bool, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Clear all stored memories in current file after user confirmation;ask twice the user for confimation.

        :param user_confirmation: Boolean indicating user confirmation to clear memories.
        :return: A message indicating the status of the operation.
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit(
            "Attempting to clear all memory entries.", status="clear_memory_attempt"
        )

        if self.confirmation_pending and user_confirmation:
            self.memory.clear_memory()
            await emitter.emit(
                description="All memory entries have been cleared.",
                status="clear_memory_complete",
                done=True,
            )
            self.confirmation_pending = False
            return json.dumps(
                {"message": "All memory entries cleared."}, ensure_ascii=False
            )

        if not self.confirmation_pending:
            self.confirmation_pending = True
            await emitter.emit(
                description="Please confirm that you want to clear all memories. Call this function again with confirmation.",
                status="confirmation_required",
                done=False,
            )
            return json.dumps(
                {"message": "Please confirm to clear all memories."}, ensure_ascii=False
            )

        await emitter.emit(
            description="Clear memory operation aborted.",
            status="clear_memory_aborted",
            done=True,
        )
        self.confirmation_pending = False
        return json.dumps(
            {"message": "Memory clear operation aborted."}, ensure_ascii=False
        )

    async def refresh_memory(self, __event_emitter__: Callable[[dict], Any] = None):
        """
        Periodically refresh and optimize memory data, includes reindexing.

        :returns: A message indicating the status of the refresh operation.
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit("Starting memory refresh process.")

        if self.valves.DEBUG:
            print("Refreshing memory...")

        if self.valves.USE_MEMORY:
            refresh_message = self.memory.reindex_memory()

            if self.valves.DEBUG:
                print(refresh_message)

            await emitter.emit(
                description=refresh_message, status="memory_refresh", done=True
            )

            return refresh_message

        if self.valves.DEBUG:
            print("Memory refreshed.")

        await emitter.emit(
            status="complete", description="Memory refresh completed.", done=True
        )

    async def update_memory_entry(
        self,
        index: int,
        tag: str,
        memo: str,
        by: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Update an existing memory entry based on its index.

        :param index: The index of the memory entry to update,STARTING FROM 1.
        :param tag: The tag for the memory entry.
        :param memo: The memory information to update.
        :param by: Who is making the update ('user' or 'LLM').
        :returns: A message indicating the success or failure of the update.
        """
        emitter = EventEmitter(__event_emitter__)

        if self.valves.DEBUG:
            print(
                f"Updating memory index {index} with tag: {tag}, memo: {memo}, by: {by}"
            )

        update_message = self.memory.update_memory_by_index(index, tag, memo, by)

        await emitter.emit(
            description=update_message, status="memory_update", done=True
        )

        return update_message

    async def add_multiple_memories(
        self,
        memory_entries: list,
        llm_wants_to_add: bool,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Allows the LLM to add multiple memory entries at once.

        :param memory_entries: A list of dictionary entries, each containing tag, memo, by.Usage Example: memory_entries = [{"tag": "personal", "memo": "This is a personal note", "by": "LLM"},{"tag": "work", "memo": "Project deadline is tomorrow", "by": "LLM"}]
        :param llm_wants_to_add: Boolean indicating LLM's desire to add the memories.
        :returns: A message indicating the success or failure of the operations.
        """
        emitter = EventEmitter(__event_emitter__)
        responses = []

        if not llm_wants_to_add:
            return "LLM has not requested to add multiple memories."

        for idx, entry in enumerate(memory_entries):
            tag = entry.get("tag", "others")
            memo = entry.get("memo", "")
            by = entry.get("by", "LLM")

            if tag not in self.memory.tag_options:
                tag = "others"

            if self.valves.DEBUG:
                print(f"Adding memory {idx+1}: tag={tag}, memo={memo}, by={by}")

            # Add the memory
            self.memory.add_to_memory(tag, memo, by)
            response = f"Memory {idx+1} added with tag {tag} by {by}."
            responses.append(response)

            await emitter.emit(description=response, status="memory_update", done=False)

        await emitter.emit(
            description="All requested memories have been processed.",
            status="memory_update_complete",
            done=True,
        )

        return "\n".join(responses)

    async def delete_memory_entry(
        self,
        index: int,
        llm_wants_to_delete: bool,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Delete a memory entry based on its index.

        :param index: The index of the memory entry to delete,STARTING FROM 1.
        :param llm_wants_to_delete: Boolean indicating if the LLM has requested the deletion.
        :returns: A message indicating the success or failure of the deletion.
        """
        emitter = EventEmitter(__event_emitter__)

        if not llm_wants_to_delete:
            return "LLM has not requested to delete a memory."

        if self.valves.DEBUG:
            print(f"Attempting to delete memory at index {index}")

        deletion_message = self.memory.delete_memory_by_index(index)

        await emitter.emit(
            description=deletion_message, status="memory_deletion", done=True
        )

        return deletion_message

    async def delete_multiple_memories(
        self,
        indices: list,
        llm_wants_to_delete: bool,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Delete multiple memory entries based on their indices.

        :param indices: A list of indices of the memory entries to delete,STARTING FROM 1.
        :param llm_wants_to_delete: Boolean indicating if the LLM has requested the deletions.
        :returns: A message indicating the success or failure of the deletions.
        """
        emitter = EventEmitter(__event_emitter__)
        responses = []

        if not llm_wants_to_delete:
            return "LLM has not requested to delete multiple memories."

        for index in indices:
            if self.valves.DEBUG:
                print(f"Attempting to delete memory at index {index}")

            deletion_message = self.memory.delete_memory_by_index(index)
            responses.append(deletion_message)

            await emitter.emit(
                description=deletion_message, status="memory_deletion", done=False
            )

        await emitter.emit(
            description="All requested memory deletions have been processed.",
            status="memory_deletion_complete",
            done=True,
        )

        return "\n".join(responses)

    async def create_or_switch_memory_file(
        self, new_file_name: str, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Create a new memory file or switch to an existing one.

        :param new_file_name: The name of the new or existing memory file.
        :returns: A message indicating the success or failure of the operation.
        """
        emitter = EventEmitter(__event_emitter__)

        if self.valves.DEBUG:
            print(f"Switching to or creating memory file: {new_file_name}")

        self.memory.switch_memory_file(new_file_name + ".json")

        message = f"Memory file switched to {new_file_name}."

        await emitter.emit(description=message, status="file_switching", done=True)

        return message

    async def list_memory_files(
        self, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        List available memory files in the current directory.

        :returns: A message with the list of available memory files.
        """
        emitter = EventEmitter(__event_emitter__)
        memory_files = []

        if self.valves.DEBUG:
            print("Listing memory files in current directory: ")

        try:
            for file in os.listdir("."):
                if file.endswith(".json"):
                    if self.valves.DEBUG:
                        print(f"Found memory file: {file}")
                    memory_files.append(file)

            description = "Available memory files: " + ", ".join(memory_files)
            status = "file_listing_complete"

        except Exception as e:
            description = f"Error accessing directory: {str(e)}"
            status = "file_listing_error"

        await emitter.emit(description=description, status=status, done=True)

        return description

    async def current_memory_file(
        self, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Retrieve the name of the currently active memory file.

        :returns: A message indicating the current memory file.
        """
        emitter = EventEmitter(__event_emitter__)

        current_file = self.memory.memory_file

        message = f"Currently using memory file: {current_file}"

        if self.valves.DEBUG:
            print(message)

        await emitter.emit(
            description=message, status="current_file_retrieved", done=True
        )

        return message

    async def delete_memory_file(
        self,
        file_to_delete: str,
        user_confirmation: bool,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Delete a memory file with confirmation and necessary file switching.

        :param file_to_delete: The name of the memory file to delete.
        :param user_confirmation: Boolean indicating user confirmation for deletion.
        :returns: A message indicating the success or failure of the deletion.
        """
        emitter = EventEmitter(__event_emitter__)
        available_files = [f for f in os.listdir(".") if f.endswith(".json")]

        if file_to_delete not in available_files:
            message = f"File '{file_to_delete}' does not exist."
            await emitter.emit(description=message, status="file_not_found", done=True)
            if self.valves.DEBUG:
                print(message)
            return message

        if self.confirmation_pending and user_confirmation:
            try:
                if self.memory.memory_file == file_to_delete:
                    # Switch to another file before deleting the current one
                    alternative_file = next(
                        (f for f in available_files if f != file_to_delete), None
                    )
                    if not alternative_file:
                        message = (
                            "No alternative memory file to switch to. Deletion aborted."
                        )
                        await emitter.emit(
                            description=message, status="no_alternative_file", done=True
                        )
                        if self.valves.DEBUG:
                            print(message)
                        return message

                    self.memory.switch_memory_file(alternative_file)
                    switch_message = f"Switched to '{alternative_file}'. Now deleting '{file_to_delete}'."
                    await emitter.emit(
                        description=switch_message, status="file_switched", done=False
                    )
                    if self.valves.DEBUG:
                        print(switch_message)

                os.remove(file_to_delete)
                message = f"File '{file_to_delete}' deleted successfully."
                status = "file_deletion_complete"
            except Exception as e:
                message = f"Error deleting file '{file_to_delete}': {str(e)}"
                status = "deletion_error"

            await emitter.emit(description=message, status=status, done=True)
            self.confirmation_pending = False
            return message

        if not self.confirmation_pending:
            self.confirmation_pending = True
            confirmation_message = (
                "Please confirm that you want to delete the memory file. "
                "Call this function again with confirmation."
            )
            await emitter.emit(
                description=confirmation_message,
                status="confirmation_required",
                done=False,
            )
            return json.dumps(
                {
                    "message": "Please confirm to delete the memory file.",
                    "file": file_to_delete,
                },
                ensure_ascii=False,
            )

        await emitter.emit(
            description="Deletion of memory file aborted.",
            status="deletion_aborted",
            done=True,
        )
        self.confirmation_pending = False
        return json.dumps(
            {"message": "Memory file deletion aborted.", "file": file_to_delete},
            ensure_ascii=False,
        )

    async def execute_functions_sequentially(
        self,
        function_calls: list,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> dict:
        """
        Execute a series of functions in sequence.

        :param function_calls: A list of dictionaries each containing 'name' and 'params'.
                               Example: [{'name': 'handle_input', 'params': {...}}, ...]
        :returns: A dictionary with results of each function call.
        """
        emitter = EventEmitter(__event_emitter__)
        results = {}

        for call in function_calls:
            func_name = call.get("name")
            params = call.get("params", {})

            if hasattr(self, func_name) and callable(getattr(self, func_name)):
                if self.valves.DEBUG:
                    print(f"Executing function: {func_name} with params: {params}")

                await emitter.emit(
                    f"Executing {func_name}", status="function_execution", done=False
                )

                try:
                    func = getattr(self, func_name)
                    result = await func(__event_emitter__=__event_emitter__, **params)
                    results[func_name] = result

                    await emitter.emit(
                        description=f"{func_name} executed successfully.",
                        status="function_complete",
                        done=False,
                    )
                except Exception as e:
                    error_msg = f"Error executing {func_name}: {str(e)}"
                    results[func_name] = error_msg

                    await emitter.emit(
                        description=error_msg, status="function_error", done=False
                    )
            else:
                error_msg = f"Function {func_name} not found or not callable."
                results[func_name] = error_msg

                await emitter.emit(
                    description=error_msg, status="function_missing", done=False
                )

        await emitter.emit(
            description="All requested functions have been processed.",
            status="execution_complete",
            done=True,
        )

        return f"executed successfully :{results}"

