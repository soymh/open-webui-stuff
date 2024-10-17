"""
title: Memory Enhancement Tool for LLM Web UI
author: https://github.com/mhioi
version: 0.1.0
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

    def add_to_memory(self, key: str, value: Any):
        if self.debug:
            print(f"Adding to memory: {key} = {value}")
        # Ensure that new data does not overwrite the existing memory but updates it
        if key in self.memory_data and isinstance(self.memory_data[key], list):
            # Append the new value to the existing list
            self.memory_data[key].append(value)
        elif key in self.memory_data:
            # Convert existing value into list and append value
            self.memory_data[key] = [self.memory_data[key], value]
        else:
            self.memory_data[key] = [value]  # Store new entry as list
        self.save_memory()

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
        DEBUG: bool = Field(default=False, description="Enable or disable debug mode.")

    def __init__(self):
        self.valves = self.Valves()
        self.memory = MemoryFunctions(debug=self.valves.DEBUG)
        self.confirmation_pending = False

    async def handle_input(
        self,
        input_text: str,
        user_wants_to_add: bool,
        llm_wants_to_add: bool,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Summarize user input and enhance responses using memory data.

        :params input_text: The TEXT .
        :return: The response considering memory data.
        """
        emitter = EventEmitter(__event_emitter__)

        if self.valves.DEBUG:
            print(f"Handling input: {input_text}")

        await emitter.emit(f"Analyzing input for memory: {input_text}")

        if self.valves.USE_MEMORY:
            memory_info = self.memory.process_input_for_memory(input_text)

            if user_wants_to_add:
                await emitter.emit(
                    description=f"User requested to add to memory: {json.dumps(memory_info, ensure_ascii=False)}",
                    status="memory_update",
                    done=False,
                )
                self.memory.add_to_memory("user_interaction", memory_info)
                return "added to memory by user's request!"
            if llm_wants_to_add:
                await emitter.emit(
                    description=f"The LLM added to memory: {json.dumps(memory_info, ensure_ascii=False)}",
                    status="memory_update",
                    done=False,
                )
                self.memory.add_to_memory("llm_interaction", memory_info)
                return "added to memory by automatic llm request!"

            # Automatically add important data
            important_data_info = {"example_key": "Important data to add"}
            self.memory.add_important_data(important_data_info)

            # Update memory if contradictions are found
            self.memory.update_memory_on_contradiction("example_key", "Updated value")

        last_interaction = self.memory.retrieve_from_memory("user_interaction")
        if last_interaction:
            await emitter.emit(
                description=f"Retrieved memory: {json.dumps(last_interaction, ensure_ascii=False)}",
                status="memory_retrieval",
                done=False,
            )

        response_message = "Response generated based on input and memory."
        if last_interaction:
            response_message += (
                f"\nLast interaction noted at: {last_interaction[-1]['timestamp']}."
            )

        await emitter.emit(
            status="complete",
            description="Processed input and handled memory operations.",
            done=True,
        )

        if self.valves.DEBUG:
            print(f"Response message: {response_message}")

        return json.dumps({"response": response_message}, ensure_ascii=False)

    async def recall_memories(
        self, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Retrieve all stored memories and provide them to the user.

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
        Clear all stored memories after user confirmation;ask twice the user for confimation.

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
        Periodically refresh and optimize memory data.
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit("Starting memory refresh process.")

        if self.valves.DEBUG:
            print("Refreshing memory...")

        if self.valves.USE_MEMORY:
            pass  # Implement any periodic memory cleanup here

        if self.valves.DEBUG:
            print("Memory refreshed.")

        await emitter.emit(
            status="complete", description="Memory refresh completed.", done=True
        )


# Example of usage: instantiate Tools and call handle_input, recall_memories, or clear_memories with user queries.

