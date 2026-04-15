#!/usr/bin/env python3

import sys
import subprocess
import os

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from sessions import *

from dotenv import load_dotenv

load_dotenv()

COMMANDS = [
    "help",
    "exit",
    "sessions",
    "sessions_refresh",
    "sessions_list",
    "sessions_create",
    "sessions_use",
    "sessions_delete",
    "sessions_nuke",
    "sessions_shell",
    "sessions_exec",
    "sessions_start",
    "sessions_stop",
    "sessions_ps",
    "launch_claude",
]

BANNER = r"""

   █████████  ████                           █████          ███████████                            
  ███░░░░░███░░███                          ░░███          ░░███░░░░░███                           
 ███     ░░░  ░███   ██████   █████ ████  ███████   ██████  ░███    ░███ █████ ███ █████ ████████  
░███          ░███  ░░░░░███ ░░███ ░███  ███░░███  ███░░███ ░██████████ ░░███ ░███░░███ ░░███░░███ 
░███          ░███   ███████  ░███ ░███ ░███ ░███ ░███████  ░███░░░░░░   ░███ ░███ ░███  ░███ ░███ 
░░███     ███ ░███  ███░░███  ░███ ░███ ░███ ░███ ░███░░░   ░███         ░░███████████   ░███ ░███ 
 ░░█████████  █████░░████████ ░░████████░░████████░░██████  █████         ░░████░████    ████ █████
  ░░░░░░░░░  ░░░░░  ░░░░░░░░   ░░░░░░░░  ░░░░░░░░  ░░░░░░  ░░░░░           ░░░░ ░░░░    ░░░░ ░░░░░ 

                    ClaudePwn  2026 |  by: ph0neh0me

Use this CLI to manage Kali sessions (Docker containers).

Inside Claude Code, you'll talk to me like this:

  agent_run nmap -sV 10.10.10.10
  agent_enumerate 10.10.10.10
  agent_exploit 10.10.10.10

"""

GLOBAL_HELP = """
Global Commands:
  help               Show this help
  sessions           Show session command help
  launch_claude      Open Claude Desktop (or your file explorer) on this project
  exit               Quit the tool
"""


def launch_claude():
    project_root = Path(__file__).resolve().parent

    # Start Claude Code
    claude_bin = os.getenv("CLAUDE_PATH", "claude")
    subprocess.Popen([claude_bin], cwd=str(project_root))

    print("[+] Claude Code launched.")
    print("[+] Leaving ClaudePwn terminal open.")
    print("[*] Manually place windows however you prefer.")


def handle_command(cmd: str):
    parts = cmd.strip().split()
    if not parts:
        return

    if parts[0] == "help" and len(parts) == 1:
        print(GLOBAL_HELP)
        return

    if parts[0] == "sessions" and len(parts) == 1:
        sessions_help()
        return

    if parts[0] == "sessions_refresh":
        if len(parts) == 1:
            sessions_refresh()
            return
        else:
            print("USAGE: sessions_refresh")
            return

    if parts[0] == "sessions_create":
        if len(parts) == 2:
            sessions_create(parts[1])
            return
        else:
            print("USAGE: sessions_create <name>")
            return

    if parts[0] == "sessions_use":
        if len(parts) == 2:
            sessions_use(parts[1])
            return
        else:
            print("USAGE: sessions_use <name>")
            return

    if parts[0] == "sessions_delete":
        if len(parts) == 2:
            sessions_delete(parts[1])
            return
        else:
            print("USAGE: sessions_delete <name>")
            return

    if parts[0] == "sessions_list":
        if len(parts) == 1:
            list_sessions()
            return
        else:
            print("USAGE: sessions_list")
            return

    if parts[0] == "sessions_nuke":
        if len(parts) == 1:
            sessions_nuke()
            return
        else:
            print("USAGE: sessions_nuke")
            return

    if parts[0] == "sessions_shell":
        sessions_shell()
        return

    if parts[0] == "sessions_exec":
        if len(parts) >= 2:
            command = " ".join(parts[1:])
            sessions_exec(command)
            return
        else:
            print("USAGE: sessions_exec <command>")
            return

    if parts[0] == "sessions_start":
        sessions_start()
        return

    if parts[0] == "sessions_stop":
        sessions_stop()
        return

    if parts[0] == "sessions_ps":
        sessions_ps()
        return

    if parts[0] == "launch_claude":
        launch_claude()
        return

    if parts[0] == "exit" and len(parts) == 1:
        print("Bye.")
        sys.exit(0)

    print(f"[!] Unknown command: {cmd}")


completer = WordCompleter(COMMANDS, ignore_case=True)


def main():
    print(BANNER)

    session = PromptSession(
        history=FileHistory(".claudepwn_history"),
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
    )

    while True:
        try:
            cmd = session.prompt("ClaudePwn> ")
            handle_command(cmd)
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
