import os
import pytest
import sys
from unittest.mock import patch, MagicMock
from bgpt.main import main_cli
import re

def strip_ansi(text):
    print(f"input text: {text}")
    stripped_text = re.sub(r'(?:\x1b|\033)\[[0-9;]*m', '', text)
    print(f"stripped text before return: {stripped_text}")
    return stripped_text

@patch("os.getenv", return_value="test_api_key")
@patch("bgpt.main.openai.OpenAI")
@patch("builtins.input", side_effect=["a", "some clarification", ""])
@patch("bgpt.main.process_command")
@patch("sys.argv", ["bgpt", "create folder test_folder"])
def test_create_folder_ai_clarify(mock_process_command, mock_input, mock_openai_class, mock_getenv, capsys):
    dummy_client = MagicMock()
    mock_message1 = MagicMock()
    mock_message1.content = "mkdir test_folder"
    
    mock_message2 = MagicMock()
    mock_message2.content = "mkdir test_folder_acl"
    
    dummy_client.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=mock_message1)]),
        MagicMock(choices=[MagicMock(message=mock_message2)])
    ]
    mock_openai_class.return_value = dummy_client
    main_cli()  # Run the command-line interface function
    captured = capsys.readouterr()
    clean_output = strip_ansi(captured.out)
    # Assert that both commands were printed (after stripping ANSI codes)
    assert "Generated bash command: mkdir test_folder" in clean_output
    assert "Generated bash command: mkdir test_folder_acl" in clean_output
    # Assert that process_command was called with the second command
    mock_process_command.assert_called_with("mkdir test_folder_acl")

@patch("sys.argv", ["bgpt", "ls"])
@patch("builtins.input", side_effect=[""])  # Simulate pressing Enter to execute
@patch("bgpt.main.openai.OpenAI")
@patch("bgpt.main.process_command")
def test_bgpt_command_no_edit(mock_process_command, mock_openai_class, mock_input, capsys):
    dummy_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "ls"
    
    dummy_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )
    mock_openai_class.return_value = dummy_client
    main_cli()
    captured = capsys.readouterr()
    clean_output = strip_ansi(captured.out)
    assert "Generated bash command: ls" in clean_output
    mock_process_command.assert_called_with("ls")

def test_strip_ansi():
    text_with_ansi = "\x1b[31mThis is red text\x1b[0m"
    print(f"text_with_ansi: {text_with_ansi}")
    stripped_text = strip_ansi(text_with_ansi)
    print(f"stripped_text: {stripped_text}")
    assert stripped_text == "This is red text"
