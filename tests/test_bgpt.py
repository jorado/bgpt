import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import re
import requests # Required for requests.exceptions.RequestException

# Assuming bgpt.main is accessible, adjust if your structure is different
from bgpt.main import main_cli, CYAN, RED, RESET # Import colors for more precise error message matching if needed

def strip_ansi(text):
    """Removes ANSI escape codes from a string."""
    return re.sub(r'(?:\x1b|\033)\[[0-9;]*m', '', text)

class TestBgptMain(unittest.TestCase):

    def setUp(self):
        # Clear os.environ mocks between tests if necessary, though patch.dict handles this well
        pass

    @patch('bgpt.main.get_bash_command_from_api')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True)
    @patch('sys.stdout', new_callable=unittest.mock.StringIO)
    def test_main_cli_success(self, mock_stdout, mock_get_bash_command_from_api):
        mock_get_bash_command_from_api.return_value = "echo 'test command'"
        
        test_args = ["bgpt", "translate", "this", "to", "bash"]
        with patch.object(sys, 'argv', test_args):
            main_cli()
        
        output = strip_ansi(mock_stdout.getvalue().strip())
        self.assertEqual(output, "echo 'test command'")
        mock_get_bash_command_from_api.assert_called_once_with(
            "translate this to bash", 
            os.getenv("LLM_MODEL", "GPT-4.1-mini"), 
            "test_key",
            os.getenv("OPENAI_BASE_URL")
        )

    @patch('bgpt.main.get_bash_command_from_api') # Still mock it to ensure it's not called
    @patch.dict(os.environ, {}, clear=True) # Ensure OPENAI_API_KEY is not set
    @patch('sys.stdout', new_callable=unittest.mock.StringIO)
    def test_main_cli_no_api_key(self, mock_stdout, mock_get_bash_command_from_api):
        test_args = ["bgpt", "some", "query"]
        with patch.object(sys, 'argv', test_args):
            main_cli()
        
        expected_error_message = f"{RED}Error: OPENAI_API_KEY environment variable not set. Please set OPENAI_API_KEY environment variable.{RESET}"
        # Output is to stdout as per current main.py
        self.assertEqual(strip_ansi(mock_stdout.getvalue().strip()), strip_ansi(expected_error_message))
        mock_get_bash_command_from_api.assert_not_called()

    @patch('bgpt.main.get_bash_command_from_api')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True)
    @patch('sys.stderr', new_callable=unittest.mock.StringIO) # Errors go to stderr
    def test_main_cli_api_error(self, mock_stderr, mock_get_bash_command_from_api):
        mock_get_bash_command_from_api.side_effect = requests.exceptions.RequestException("API is down")
        
        test_args = ["bgpt", "another", "query"]
        with patch.object(sys, 'argv', test_args):
            main_cli()
        
        # Check that the error message includes the specific exception message
        # As per main.py: print(f"{RED}API request error: {e}. Check your OPENAI_API_KEY and BASE_URL.{RESET}", file=os.sys.stderr)
        captured_error = strip_ansi(mock_stderr.getvalue().strip())
        self.assertIn("API request error: API is down.", captured_error)
        self.assertIn("Check your OPENAI_API_KEY and BASE_URL.", captured_error)
        mock_get_bash_command_from_api.assert_called_once()

    @patch('bgpt.main.get_bash_command_from_api')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True)
    @patch('sys.stderr', new_callable=unittest.mock.StringIO) # Errors go to stderr
    def test_main_cli_unexpected_error(self, mock_stderr, mock_get_bash_command_from_api):
        mock_get_bash_command_from_api.side_effect = Exception("Something broke badly")

        test_args = ["bgpt", "unexpected", "query"]
        with patch.object(sys, 'argv', test_args):
            main_cli()

        # As per main.py: print(f"{RED}An unexpected error occurred: {e}{RESET}", file=os.sys.stderr)
        captured_error = strip_ansi(mock_stderr.getvalue().strip())
        self.assertIn("An unexpected error occurred: Something broke badly", captured_error)
        mock_get_bash_command_from_api.assert_called_once()

    def test_strip_ansi_utility(self):
        text_with_ansi = "\x1b[96mHello\x1b[0m World"
        self.assertEqual(strip_ansi(text_with_ansi), "Hello World")
        text_without_ansi = "Hello World"
        self.assertEqual(strip_ansi(text_without_ansi), "Hello World")
        empty_text = ""
        self.assertEqual(strip_ansi(empty_text), "")

if __name__ == '__main__':
    unittest.main()
