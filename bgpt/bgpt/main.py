import argparse
import os
import urllib.request
import json
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
    api_url = base_url + "/chat/completions"
    data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        response_data = response.read().decode('utf-8')
    return json.loads(response_data)['choices'][0]['message']['content'].strip()

def get_user_choice(bash_command):
    print(f"Generated bash command: {CYAN}{bash_command}{RESET}")
    prompt = f"{YELLOW}Execute command? {RESET}(press Enter to execute, 'a' to edit with AI, or any other key to cancel):"
    return input(prompt).lower()

def main_cli():
    parser = argparse.ArgumentParser(description="bgpt: Convert natural language to bash commands")
    parser.add_argument("command_text", nargs="+", help="Natural language command to convert to bash")
    args = parser.parse_args()
    command_text = " ".join(args.command_text)

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL", "GPT-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") # Set default base_url
    if not api_key:
        print(f"{RED}Error: OPENAI_API_KEY environment variable not set. Please set OPENAI_API_KEY environment variable.{RESET}")
        return

    try:
        bash_command = get_bash_command_from_api(command_text, model, api_key, base_url)
        while True:
            user_choice = get_user_choice(bash_command)
            if user_choice == "":  # Enter - Execute
                process_command(bash_command, command_text)
                break
            elif user_choice == 'a':  # edit with AI
                clarification_text = input(f"{YELLOW}Enter desired changes in natural language: {RESET}")
                command_text += " " + clarification_text
                bash_command = get_bash_command_from_api(command_text, model, api_key, base_url)
            else:  # Cancel
                print(f"{YELLOW}Command execution cancelled.{RESET}")
                break

    except Exception as e:
        print(f"{RED}API request error: {e}. Check your OPENAI_API_KEY and BASE_URL.{RESET}")
    except Exception as e:
        print(f"{RED}An unexpected error occurred: {e}{RESET}")


def process_command(command, original_command_text):
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            print(f"{GREEN}> {command} {RESET}")
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(f"{RED}Error output for command: {original_command_text}:{RESET}") # Include original command text in error message
            print(process.stderr)
    except FileNotFoundError:
        print(f"{RED}Command not found: {command}{RESET}")
    except Exception as e:
        print(f"{RED}Error executing command: {e}{RESET}")

if __name__ == "__main__":
    main_cli()
