# bgpt - Bash GPT CLI Tool

A command-line tool that translates natural language commands into bash commands using OpenAI's language models.

## Installation

```bash
pip install .
```

## Usage

Before using `bgpt`, make sure you have the `OPENAI_API_KEY` environment variable set with your OpenAI API key. You can also set the `OPENAI_BASE_URL` environment variable if you are using a custom OpenAI endpoint, and the `LLM_MODEL` environment variable to change the model. The default model is GPT-4.1-mini.

Example:
\`\`\`bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="GPT-4.1-mini"
\`\`\`

```bash
bgpt <natural language command>
```

**Examples:**

```bash
bgpt create a folder named my-folder
bgpt list all files in the current directory
bgpt show me the contents of my_file.txt
```

The tool will then:

1. Generate a bash command based on your input.
2. Display the generated command and ask for confirmation.
3. Execute the command if you confirm.
4. Show the output of the command.

## Configuration

-   **OPENAI\_API_KEY:** You must set this environment variable to your OpenAI API key.
-   **OPENAI\_BASE_URL:** (Optional) Set this environment variable if you are using a custom OpenAI endpoint.
-   **LLM_MODEL:** (Optional) Set this environment variable to change the model.

## Dependencies

-   Python 3.8+
-   openai Python library

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please submit a pull request with your changes.

## Code of Conduct

Please note that this project is released with a [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/) Code of Conduct. By participating in this project you agree to abide by its terms.

---
**Note:** This tool uses the OpenAI API, so usage will incur costs based on your OpenAI API billing. Please use responsibly.
