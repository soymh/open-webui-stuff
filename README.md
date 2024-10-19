# Memory Enhancement Tool for Open WebUI

**Author**: [mhioi](https://github.com/mhioi)  
**Version**: 1.4.0  
**License**: MIT  

This repository provides a powerful memory management enhancement tool for a local large language model (LLM) web UI. It offers a series of functionalities to handle memory files and provide interactions through an easy-to-use API. Below you'll find a detailed overview of each function within the `Tools` class, along with sample usage commands.

## Installation

1st way. Go to [this](https://openwebui.com/t/mhio/gpt4_memory_mimic) link and install.

2nd way. Navigate into the tools directory in this project,download json file of the tool and import it in the tools section of your open WebUI.

## Usage of Tools Class Functions By the LLM

### handle_input

**Description**: Automatically summarize user input and enhance responses using memory data. 

**Command**: *Handle input of "X" as a memory with the tag "Y" in the current memory file.*

```python
await tools.handle_input(
    input_text="X",
    tag="Y",
    user_wants_to_add=True,  # or False if not adding
    llm_wants_to_add=False,  # or True if LLM adds
    by="user"
)
```

### recall_memories

**Description**: Retrieve all stored memories in the current file and provide them to the user.

**Command**: *Recall all memories stored in the current file.*

```python
await tools.recall_memories()
```

### clear_memories

**Description**: Clear all stored memories in the current file after user confirmation (requires confirmation twice).

**Command**: *Clear all memories in the current file after two confirmations.*

```python
await tools.clear_memories(user_confirmation=True)  # Call twice with True after initial confirmation.
```

### refresh_memory

**Description**: Refresh and optimize memory data, including reindexing.

**Command**: *Refresh and optimize the memory data, including reindexing operations.*

```python
await tools.refresh_memory()
```

### update_memory_entry

**Description**: Update an existing memory entry based on its index.

**Command**: *Update memory entry with index X to have tag "Y" and memo "Z" by user.*

```python
await tools.update_memory_entry(index=X, tag="Y", memo="Z", by="user")
```

### add_multiple_memories

**Description**: Add multiple memory entries simultaneously.

**Command**: *Add multiple memories with specified tags and memos in the current memory file.*

```python
await tools.add_multiple_memories(
    memory_entries=[
        {"tag": "personal", "memo": "First note", "by": "user"},
        {"tag": "work", "memo": "Project update", "by": "LLM"}
    ],
    llm_wants_to_add=True
)
```

### delete_memory_entry

**Description**: Delete a specific memory entry based on its index after confirmation.

**Command**: *Delete the memory entry at index X after confirming deletion.*

```python
await tools.delete_memory_entry(index=X, llm_wants_to_delete=True)
```

### delete_multiple_memories

**Description**: Delete multiple memory entries in one go based on their indices.

**Command**: *Delete multiple memory entries specified by their indices.*

```python
await tools.delete_multiple_memories(indices=[1, 3, 5], llm_wants_to_delete=True)
```

### create_or_switch_memory_file

**Description**: Create a new memory file or switch to an existing one.

**Command**: *Switch to a new or existing memory file named "file_name".*

```python
await tools.create_or_switch_memory_file("file_name")
```

### list_memory_files

**Description**: List all available memory files in the designated directory.

**Command**: *List all memory files available in the working directory.*

```python
await tools.list_memory_files()
```

### current_memory_file

**Description**: Retrieve the name of the currently active memory file.

**Command**: *Fetch the name of the currently active memory file.*

```python
await tools.current_memory_file()
```

### delete_memory_file

**Description**: Delete a memory file with user confirmation and necessary file switching.

**Command**: *Delete a memory file after confirming and managing active file switching.*

```python
await tools.delete_memory_file(
    file_to_delete="file_name.json",
    user_confirmation=True  # Call twice with True for confirmation.
)
```

### execute_functions_sequentially

**Description**: Execute a series of functions in sequence.

**Command**: *Execute a sequence of functions as planned.*

```python
await tools.execute_functions_sequentially(
    function_calls=[
        {"name": "handle_input", "params": {"input_text": "Example", "tag": "work"}},
        {"name": "recall_memories", "params": {}}
    ]
)
```
### Future updates:
#### download_memory_file

**Description**: Provide a download link for a memory file, or archive all memory files for download.

**Command**: *Download the specified memory file or archive all as a tar for download.*

```python
await tools.download_memory_file(port=8080, file_name="memory.json")
await tools.download_memory_file(port=8080, all_files=True)
```

## Contributing

Contributions are welcome! Please fork the repository and submit your pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
