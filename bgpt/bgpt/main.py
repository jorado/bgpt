import argparse
import os
import requests
import subprocess

# ANSI Color Codes
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"

def get_bash_command_from_api(command_text, model, api_key, base_url):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a bgpt that translates natural language commands into bash."},
            {"role": "user", "content": "Only respond with the bash command, do not include any other text or explanations. E.g.: if I ask: 'Create a folder with the name test-folder', you must only output: 'mkdir test-folder'. \n \n " + command_text},
        ],
        "temperature": 0.1,
    }
    api_url = base_url + "/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"
    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()

def main_cli():
    parser = argparse.ArgumentParser(description="bgpt: Convert natural language to bash commands")
    parser.add_argument("command_text", nargs="+", help="Natural language command to convert to bash")
    args = parser.parse_args()
    command_text = " ".join(args.command_text)

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL", "GPT-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        print(f"{RED}Error: OPENAI_API_KEY environment variable not set. Please set OPENAI_API_KEY environment variable.{RESET}")
        return

    try:
        bash_command = get_bash_command_from_api(command_text, model, api_key, base_url)
        print(f"{CYAN}{bash_command}{RESET}")  # Print the bash command

    except requests.exceptions.RequestException as e:
        # Print API errors to stderr
        print(f"{RED}API request error: {e}. Check your OPENAI_API_KEY and BASE_URL.{RESET}", file=os.sys.stderr)
    except Exception as e:
        # Print other unexpected errors to stderr
        print(f"{RED}An unexpected error occurred: {e}{RESET}", file=os.sys.stderr)

# No process_command function here anymore

if __name__ == "__main__":
    main_cli()
