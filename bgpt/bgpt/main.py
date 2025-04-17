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

def main_cli():
    parser = argparse.ArgumentParser(description="bgpt: Convert natural language to bash commands")
    parser.add_argument("command_text", nargs="+", help="Natural language command to convert to bash")
    args = parser.parse_args()
    command_text = " ".join(args.command_text)

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL", "GPT-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        print(f"{RED}Error: OPENAI_API_KEY environment variable not set.{RESET}")
        return

    try:
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
        response.raise_for_status()  # Raise an exception for HTTP errors

        bash_command = response.json()['choices'][0]['message']['content'].strip()

        print(f"Generated bash command: {CYAN}{bash_command}{RESET}")
        prompt = f"{YELLOW}Execute command? {RESET}(press Enter to execute, 'a' to edit with AI, or any other key to cancel):"
        user_choice = input(prompt).lower()

        if user_choice == "": # Enter - Execute
            process_command(bash_command)
        elif user_choice == 'a': # edit with AI
            clarification_text = input(f"{YELLOW}Enter desired changes in natural language: {RESET}")
            new_command_text = command_text + " " + clarification_text
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a bgpt that translates natural language commands into bash."},
                        {"role": "user", "content": "Only respond with the bash command, do not include any other text or explanations. E.g.: if I ask: 'Create a folder with the name test-folder', you must only output: 'mkdir test-folder'. \n \n " + new_command_text},
                    ],
                    "temperature": 0.1,
                }

                response = requests.post(api_url, headers=headers, json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors
                bash_command = response.json()['choices'][0]['message']['content'].strip()
                print(f"Generated bash command: {CYAN}{bash_command}{RESET}")
                prompt = f"{YELLOW}Execute command? {RESET}(press Enter to execute, any other key to cancel):"
                user_choice = input(prompt).lower()

                if user_choice == "": # Enter - Execute
                    process_command(bash_command)
                elif user_choice == 'a': # edit with AI (recursive call) - Limit recursion
                    print(f"{YELLOW}edit with AI selected again. To avoid infinite loop, cancelling.{RESET}")
                else: # Cancel
                    print(f"{YELLOW}Command execution cancelled.{RESET}")

            except requests.exceptions.RequestException as e:
                print(f"{RED}API request error: {e}{RESET}")
            except Exception as e:
                print(f"{RED}An error occurred: {e}{RESET}")
        else: # Cancel
            print(f"{YELLOW}Command execution cancelled.{RESET}")

    except requests.exceptions.RequestException as e:
        print(f"{RED}API request error: {e}{RESET}")
    except Exception as e:
        print(f"{RED}An unexpected error occurred: {e}{RESET}")

def process_command(command):
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True) 
        if process.returncode == 0:
            print(f"{GREEN}> {command} {RESET}")
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(f"{RED}Error output:{RESET}")
            print(process.stderr)
    except FileNotFoundError:
        print(f"{RED}Command not found: {command}{RESET}")
    except Exception as e:
        print(f"{RED}Error executing command: {e}{RESET}")

if __name__ == "__main__":
    main_cli()
