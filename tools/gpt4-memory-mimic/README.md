
# Memory Enhancement Tool for Open WebUI- GPT4-Memory-Mimic

## Overview

### Developed by: soymh
### Latest Release: 1.5.0  
### License: MIT

Seeking a seamless memory management experience for your local Large Language Model (LLM) web UI? Look no further! The Memory Enhancement Tool for Open WebUI is your go-to solution, offering a streamlined suite of features through a simple API.

## Installation Guide

### Quick Start

- [Explore Installation Instructions](https://openwebui.com/t/mhio/gpt4_memory_mimic)

### Manual Setup

- Download the `Tools` directory's JSON file, importing it into the tools section of your Open WebUI.

## Explore the Functions

### `handle_input`

- **Purpose**: Intelligently summarizes user input to improve AI responses using memory content.
- **Usage Example**: `await tools.handle_input(input_text="X", tag="Y", user_wants_to_add=True, llm_wants_to_add=False, by="user")`

### `recall_memories`

- **Purpose**: Fetches and presents all stored memories.
- **Usage Example**: `await tools.recall_memories()`

### `clear_memories`

- **Purpose**: Permanently deletes all memories post-double confirmation.
- **Usage Example**: `await tools.clear_memories(user_confirmation=True)`

### `refresh_memory`

- **Purpose**: Reorganizes and optimizes memory data.
- **Usage Example**: `await tools.refresh_memory()`

### `update_memory_entry`

- **Purpose**: Modifies an existing memory entry by index.
- **Usage Example**: `await tools.update_memory_entry(index=X, tag="Y", memo="Z", by="user")`

### `add_multiple_memories`

- **Purpose**: Adds multiple memory entries in one action.
- **Usage Example**: `await tools.add_multiple_memories(memory_entries=[{"tag": "personal", "memo": "First note", "by": "user"}, {"tag": "work", "memo": "Project update", "by": "LLM"}], llm_wants_to_add=True)`

### `delete_memory_entry`

- **Purpose**: Removes a memory entry by index, with confirmation.
- **Usage Example**: `await tools.delete_memory_entry(index=X, llm_wants_to_delete=True)`

### `delete_multiple_memories`

- **Purpose**: Deletes multiple entries by index.
- **Usage Example**: `await tools.delete_multiple_memories(indices=[1, 3, 5], llm_wants_to_delete=True)`

### `create_or_switch_memory_file`

- **Purpose**: Creates or transitions to a specified memory file.
- **Usage Example**: `await tools.create_or_switch_memory_file("file_name")`

### `list_memory_files`

- **Purpose**: Displays all available memory files.
- **Usage Example**: `await tools.list_memory_files()`

### `current_memory_file`

- **Purpose**: Reveals the active memory file.
- **Usage Example**: `await tools.current_memory_file()`

### `delete_memory_file`

- **Purpose**: Permanently deletes a memory file after confirmation.
- **Usage Example**: `await tools.delete_memory_file(file_to_delete="file_name.json", user_confirmation=True)`

### `execute_functions_sequentially`

- **Purpose**: Sequentially executes a series of functions.
- **Usage Example**: `await tools.execute_functions_sequentially(function_calls=[{"name": "handle_input", "params": {"input_text": "Example", "tag": "work"}}, {"name": "recall_memories", "params": {}}])`

---

## Contribute

Join our endeavor in making memory management more effective! If you're keen on contributing, consider forking the repository and forwarding your pull requests.

---

### Licensing

This project is distributed under the **MIT License**.
