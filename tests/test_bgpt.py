from unittest.mock import patch, MagicMock
from bgpt.main import main_cli
import re

def strip_ansi(text):
    print(f"input text: {text}")
    stripped_text = re.sub(r'(?:\x1b|\033)\[[0-9;]*m', '', text)
    print(f"stripped text before return: {stripped_text}")
    return stripped_text

@patch("requests.post")
@patch("builtins.input", side_effect=["a", "some clarification", ""])
@patch("bgpt.main.process_command")
@patch("sys.argv", ["bgpt", "create folder test_folder"])
@patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
def test_create_folder_ai_clarify(mock_process_command, mock_input, mock_requests_mock, capsys):
    mock_response1 = MagicMock()
    mock_response1.json.return_value = {
        "choices": [{"message": {"content": "mkdir test_folder"}}]
    }

    mock_response2 = MagicMock()
    mock_response2.json.return_value = {
        "choices": [{"message": {"content": "mkdir test_folder_acl"}}]
    }

    mock_requests_mock.side_effect = [mock_response1, mock_response2]
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
@patch("requests.post")
@patch("bgpt.main.process_command")
@patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test_key'})
def test_bgpt_command_no_edit(mock_process_command, mock_requests_mock, mock_input, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "ls"}}]
    }
    mock_requests_mock.return_value = mock_response

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
