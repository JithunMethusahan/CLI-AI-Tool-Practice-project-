
"""
OpenRouter CLI Assistant

An interactive command-line AI assistant that integrates with the OpenRouter API.
Features include model switching, file context management, conversation history,
and streaming responses with markdown formatting.
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Dict, Generator, Optional

# Attempt to import rich for markdown formatting and beautiful UI
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.panel import Panel
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class OpenRouterAssistant:
    """A command-line interface for chatting with AI models via OpenRouter API."""
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str, stream: bool):
        """
        Initialize the AI Assistant.

        Args:
            api_key (str): OpenRouter API Key.
            model (str): The default model to use.
            stream (bool): Whether to stream the responses.
        """
        self.api_key = api_key
        self.model = model
        self.stream = stream
        self.history: List[Dict[str, str]] =[]
        self.context_files: Dict[str, str] = {}
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/CLI-Assistant",  # Required by OpenRouter
            "X-Title": "Python CLI Assistant",                   # Required by OpenRouter
            "Content-Type": "application/json"
        }

    def print_system(self, text: str, style: str = "bold blue") -> None:
        """Prints a system message nicely."""
        if RICH_AVAILABLE:
            console.print(text, style=style)
        else:
            print(f"\n[SYSTEM] {text}")

    def print_error(self, text: str) -> None:
        """Prints an error message."""
        if RICH_AVAILABLE:
            console.print(text, style="bold red")
        else:
            print(f"\n[ERROR] {text}", file=sys.stderr)

    def print_welcome(self) -> None:
        """Displays the welcoming startup message."""
        welcome_msg = (
            "Welcome to the OpenRouter CLI Assistant! 🚀\n"
            f"Current Model: {self.model}\n"
            f"Streaming: {'Enabled' if self.stream else 'Disabled'}\n\n"
            "Type your prompt to chat, or type [bold cyan]/help[/bold cyan] to see available commands."
        )
        if RICH_AVAILABLE:
            console.print(Panel(welcome_msg, title="AI CLI", border_style="green"))
        else:
            print("=" * 60)
            print(" Welcome to the OpenRouter CLI Assistant! 🚀")
            print(f" Current Model: {self.model}")
            print(f" Streaming: {'Enabled' if self.stream else 'Disabled'}")
            print(" Type /help to see available commands.")
            print("=" * 60)

    def show_help(self) -> None:
        """Displays available slash commands."""
        help_text = (
            "Available Commands:\n"
            "  /help                 - Show this help message\n"
            "  /model <name>         - Switch OpenRouter model (e.g., anthropic/claude-3-haiku)\n"
            "  /add <filepath>       - Add a file's content to the AI's context\n"
            "  /remove <filename>    - Remove a file from the AI's context\n"
            "  /files                - List all files currently in the context\n"
            "  /stream               - Toggle streaming mode on/off\n"
            "  /clear                - Clear the conversation history\n"
            "  /exit, /quit          - Exit the application"
        )
        if RICH_AVAILABLE:
            console.print(Panel(help_text, title="Help", border_style="cyan"))
        else:
            print(f"\n{help_text}\n")

    def add_file(self, filepath: str) -> None:
        """Adds a file to the system context mapping."""
        if not os.path.exists(filepath):
            self.print_error(f"File not found: {filepath}")
            return
        if not os.path.isfile(filepath):
            self.print_error(f"Path is not a file: {filepath}")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            filename = os.path.basename(filepath)
            self.context_files[filename] = content
            self.print_system(f"✅ Added '{filename}' to context.")
        except Exception as e:
            self.print_error(f"Failed to read file: {e}")

    def remove_file(self, filename: str) -> None:
        """Removes a file from the system context mapping."""
        if filename in self.context_files:
            del self.context_files[filename]
            self.print_system(f"🗑️ Removed '{filename}' from context.")
        else:
            self.print_error(f"File '{filename}' is not in the context.")

    def list_files(self) -> None:
        """Lists currently loaded context files."""
        if not self.context_files:
            self.print_system("No files currently in context.")
            return
        
        files_str = "\n".join([f" - {f} ({len(c)} chars)" for f, c in self.context_files.items()])
        self.print_system(f"Files in context:\n{files_str}")

    def _build_system_prompt(self) -> str:
        """Constructs the system prompt, appending file contents if available."""
        base_prompt = (
            "You are an expert developer and AI assistant. "
            "When providing code, ensure it is functional, well-commented, "
            "and adheres to best practices. Provide brief explanations alongside the code."
        )
        if not self.context_files:
            return base_prompt

        file_contexts =[]
        for filename, content in self.context_files.items():
            file_contexts.append(f"--- BEGIN FILE: {filename} ---\n{content}\n--- END FILE: {filename} ---")
        
        return base_prompt + "\n\nHere are some files for context:\n" + "\n\n".join(file_contexts)

    def _generate_api_payload(self, user_input: str) -> dict:
        """Prepares the payload for the API request."""
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_input})

        return {
            "model": self.model,
            "messages": messages,
            "stream": self.stream
        }

    def _stream_response(self, payload: dict) -> Generator[str, None, None]:
        """Generator to handle Server-Sent Events (SSE) streaming."""
        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload, stream=True)
            
            if response.status_code == 429:
                yield "Error: Rate limit exceeded (429)."
                return
            elif response.status_code != 200:
                yield f"Error: API returned status {response.status_code} - {response.text}"
                return

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            # OpenRouter payload delta extraction
                            chunk = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            yield f"\n[Network Error]: {e}"

    def _sync_response(self, payload: dict) -> Optional[str]:
        """Handles standard, non-streaming API requests."""
        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload)
            if response.status_code == 429:
                self.print_error("Rate limit exceeded (429).")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                self.print_error("Received empty response from the API.")
                return None
            return content

        except requests.exceptions.RequestException as e:
            self.print_error(f"Network Error: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            self.print_error(f"Failed to parse API response: {e}")
            return None

    def chat(self, user_input: str) -> None:
        """Handles the chat logic, delegating to stream or sync appropriately."""
        payload = self._generate_api_payload(user_input)
        final_response = ""

        if RICH_AVAILABLE and self.stream:
            console.print()
            with Live(Markdown(""), console=console, refresh_per_second=12) as live:
                for chunk in self._stream_response(payload):
                    final_response += chunk
                    live.update(Markdown(final_response))
            console.print()

        elif self.stream:
            print("\nAI: ", end="")
            for chunk in self._stream_response(payload):
                final_response += chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print("\n")

        else:
            if RICH_AVAILABLE:
                with console.status("[bold green]Generating response...[/bold green]"):
                    final_response = self._sync_response(payload) or ""
                if final_response:
                    console.print(Markdown(final_response))
                    console.print()
            else:
                print("\nGenerating response...")
                final_response = self._sync_response(payload) or ""
                if final_response:
                    print(f"\nAI: {final_response}\n")

        if final_response and not final_response.startswith("Error:"):
            # Update history
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": final_response})

    def handle_command(self, command_line: str) -> bool:
        """
        Parses and handles slash commands.
        Returns False if the program should exit, True otherwise.
        """
        parts = command_line.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command in ("/exit", "/quit"):
            self.print_system("Goodbye! 👋")
            return False
        elif command == "/help":
            self.show_help()
        elif command == "/model":
            if not arg:
                self.print_error("Usage: /model <model_name>")
            else:
                self.model = arg
                self.print_system(f"Switched model to: {self.model}")
        elif command == "/add":
            if not arg:
                self.print_error("Usage: /add <filepath>")
            else:
                self.add_file(arg)
        elif command == "/remove":
            if not arg:
                self.print_error("Usage: /remove <filename>")
            else:
                self.remove_file(arg)
        elif command == "/files":
            self.list_files()
        elif command == "/stream":
            self.stream = not self.stream
            self.print_system(f"Streaming mode: {'Enabled' if self.stream else 'Disabled'}")
        elif command == "/clear":
            self.history.clear()
            self.print_system("Conversation history cleared.")
        else:
            self.print_error(f"Unknown command: {command}. Type /help for options.")
            
        return True

    def run(self) -> None:
        """Starts the interactive CLI loop."""
        self.print_welcome()
        
        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = console.input("[bold magenta]You:[/bold magenta] ").strip()
                else:
                    user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    should_continue = self.handle_command(user_input)
                    if not should_continue:
                        break
                else:
                    self.chat(user_input)

            except KeyboardInterrupt:
                self.print_system("\nOperation cancelled by user.")
            except EOFError:
                self.print_system("\nExiting...")
                break
            except Exception as e:
                self.print_error(f"An unexpected error occurred: {e}")


def setup_argparse() -> argparse.Namespace:
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="A command-line AI assistant powered by OpenRouter API."
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="meta-llama/llama-3-8b-instruct:free",
        help="Specify the OpenRouter model to use (default: meta-llama/llama-3-8b-instruct:free)"
    )
    parser.add_argument(
        "--no-stream", 
        action="store_true", 
        help="Disable streaming responses"
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    args = setup_argparse()
    
    # Retrieve API Key securely from Environment Variables
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        error_msg = (
            "Environment variable OPENROUTER_API_KEY is missing!\n"
            "Please set it using: export OPENROUTER_API_KEY='your_api_key_here'"
        )
        if RICH_AVAILABLE:
            console.print(error_msg, style="bold red")
        else:
            print(f"[ERROR] {error_msg}", file=sys.stderr)
        sys.exit(1)

    assistant = OpenRouterAssistant(
        api_key=api_key,
        model=args.model,
        stream=not args.no_stream
    )
    
    assistant.run()

if __name__ == "__main__":
    main()