# Memory Enhancement Tool for Open WebUI

**Author**: [mhioi](https://github.com/mhioi)  
**Version**: 1.5.0  
**License**: MIT  

Hey there! Welcome to the Memory Enhancement Tool for Open WebUI repository. Here, we're all about making memory management seamless and effective for your local LLM web UI. With this tool, you get a suite of functionalities to manage memory files and foster rich interactions through a straightforward API. Let's dive into what you can do with each function in the `Tools` class.

## Installation

Ready to get started? Here’s how you can install the tool:

1. **Quick Start**: Visit [this link](https://openwebui.com/t/mhio/gpt4_memory_mimic) and follow the install instructions.

2. **Manual Setup**: Head to the tools directory in our project, download the JSON file of the tool, and import it into the tools section of your Open WebUI.

## Using the Tools Class Functions

### handle_input

**What it does**: This function smartly summarizes user input and improves responses using memory data.

**When to use**: Whenever you want to handle input "X" tagged as "Y" in the current memory file. 

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

**What it does**: Fetch all the sweet memories you’ve stored in the current file.

**When to use**: When you need a recap of all stored memories.

```python
await tools.recall_memories()
```

### clear_memories

**What it does**: Clears all stored memories in the current file after double confirmation. 

**When to use**: Ideal for when you're ready to start fresh.

```python
await tools.clear_memories(user_confirmation=True)  # Call twice to fully confirm.
```

### refresh_memory

**What it does**: Refreshes and optimizes the memory data, keeping it organized.

**When to use**: Perfect for routine maintenance to ensure everything's running smoothly.

```python
await tools.refresh_memory()
```

### update_memory_entry

**What it does**: Updates an existing memory entry based on its index.

**When to use**: Use this for quick edits to your memories!

```python
await tools.update_memory_entry(index=X, tag="Y", memo="Z", by="user")
```

### add_multiple_memories

**What it does**: Lets you add several memory entries in one go.

**When to use**: If you’ve got a bunch of notes to add, this one’s for you!

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

**What it does**: Removes a specific memory entry based on its index, with confirmation.

**When to use**: When a memory entry has run its course and you’re ready to say goodbye.

```python
await tools.delete_memory_entry(index=X, llm_wants_to_delete=True)
```

### delete_multiple_memories

**What it does**: Delete multiple entries at once, based on their indices.

**When to use**: Clearing out several entries in a swoop? Try this!

```python
await tools.delete_multiple_memories(indices=[1, 3, 5], llm_wants_to_delete=True)
```

### create_or_switch_memory_file

**What it does**: Creates or switches to a specified memory file.

**When to use**: Whenever you need to organize your memories into a different file.

```python
await tools.create_or_switch_memory_file("file_name")
```

### list_memory_files

**What it does**: Lists all available memory files in your go-to directory.

**When to use**: Curious about what files you have? This command lists them all.

```python
await tools.list_memory_files()
```

### current_memory_file

**What it does**: Tells you which memory file is currently active.

**When to use**: A quick check-in to see where your memories are hanging out.

```python
await tools.current_memory_file()
```

### delete_memory_file

**What it does**: Deletes a memory file, with confirmation and necessary switching.

**When to use**: Use when you’ve decided you no longer need a particular file.

```python
await tools.delete_memory_file(
    file_to_delete="file_name.json",
    user_confirmation=True  # Remember to confirm twice!
)
```

### execute_functions_sequentially

**What it does**: Executes a series of functions, one after the other.

**When to use**: Planning a string of operations? Execute them seamlessly!

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

**What it does**: Offers a link to download a specified memory file or an archive of all memory files.

**When to use**: When you want to keep a local copy or share your memory files.

```python
await tools.download_memory_file(port=8080, file_name="memory.json")
await tools.download_memory_file(port=8080, all_files=True)
```

## Contributing

We’d love your help! If you’d like to contribute, please fork the repository and send in your pull requests.

## License

This project proudly operates under the MIT License. For more details, check out the [LICENSE](LICENSE) file.

Happy memory managing!
```

### Key Improvements

- **Engaging Language**: The text is designed to connect with users in a conversational tone while being informative.
  
- **Clear Usage Instructions**: Each section now pairs the description with a straightforward command to enhance understanding.

- **Consistency**: Consistent headers and descriptions guide readers through each function without unnecessary complexity.

This README is more inviting and should help users seamlessly engage with your tool.
