#!/usr/bin/env python3

# ClaudePwn - Autonomous Pentesting Framework
# Copyright (C) 2026  Petar Georgiev
# Licensed under the GPLv3. See LICENSE for details.

import os
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
CURRENT_FILE = os.path.join(SESSIONS_DIR, ".current")

CONTAINER_NAME = "claude_pwn"
IMAGE_NAME = "claude_pwn_image"

CURRENT_SESSION = None


def load_current_session():
    global CURRENT_SESSION
    if os.path.exists(CURRENT_FILE):
        with open(CURRENT_FILE, "r", encoding="utf-8") as f:
            CURRENT_SESSION = f.read().strip()


load_current_session()


def sessions_help():
    print(
        f"""
Session Info:
  Active session:  {CURRENT_SESSION if CURRENT_SESSION else "(none)"}
  Sandbox image:   {"present" if image_exists() else "Missing, use `sessions_refresh`"}
  Container name:  {CONTAINER_NAME}

Session Commands:
  sessions_refresh
  sessions_list
  sessions_create <name>
  sessions_use <name>
  sessions_delete <name>
  sessions_nuke

  sessions_shell
  sessions_exec <cmd>
  sessions_start
  sessions_stop
  sessions_ps
"""
    )


def docker_available():
    try:
        result = subprocess.run(
            ["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def container_running():
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", f"name={CONTAINER_NAME}"],
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip() != ""


def ensure_sessions_root():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def write_current_session(name: str):
    global CURRENT_SESSION
    CURRENT_SESSION = name
    ensure_sessions_root()
    with open(CURRENT_FILE, "w", encoding="utf-8") as f:
        f.write(name)


def stop_container():
    subprocess.run(
        ["docker", "rm", "-f", CONTAINER_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def image_exists():
    result = subprocess.run(
        ["docker", "images", "-q", IMAGE_NAME],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip() != ""


def start_container_with_mount(session_path: str):
    workspace = os.path.join(session_path, "workspace")
    os.makedirs(workspace, exist_ok=True)

    stop_container()

    run = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,

            "--privileged",
            "--device=/dev/net/tun",
            "--cap-add=ALL",
            "-v",
            f"{workspace}:/workspace",

            "-p",
            "8080:8080",
            "-p",
            "8000:8000",

            IMAGE_NAME,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if run.returncode != 0:
        print("[!] Failed to start container:")
        print(run.stderr.strip())
        return False

    return True


def sessions_refresh():
    ensure_sessions_root()

    if not docker_available():
        print("[!] Docker is not available. Cannot refresh.")
        return

    print("[*] Rebuilding sandbox image. This may take a few minutes...")

    build = subprocess.run(
        ["docker", "build", "--no-cache", "-t", IMAGE_NAME, BASE_DIR]
    )

    if build.returncode != 0:
        print("\n[!] Docker build failed.")
        return

    print("[+] Image built successfully.")

    if CURRENT_SESSION:
        session_path = os.path.join(SESSIONS_DIR, CURRENT_SESSION)

        if not os.path.exists(session_path):
            print("[!] Current session directory missing:", session_path)
            return

        print(f"[*] Restarting container for session '{CURRENT_SESSION}'...")
        if start_container_with_mount(session_path):
            print("[+] Container restarted.")
        else:
            print("[!] Failed to restart container.")
    else:
        print("[*] No active session.")


def list_sessions():
    ensure_sessions_root()
    sessions = sorted([s for s in os.listdir(SESSIONS_DIR) if s != ".current"])

    if not sessions:
        print("[*] No sessions found.")
        return

    for s in sessions:
        tag = " (active)" if s == CURRENT_SESSION else ""
        print(f" - {s}{tag}")


def sessions_create(name: str):
    ensure_sessions_root()
    session_path = os.path.join(SESSIONS_DIR, name)

    if os.path.exists(session_path):
        print(f"[!] Session '{name}' already exists.")
        return

    if not docker_available():
        print("[!] Docker not available.")
        return

    if not image_exists():
        print("[!] Sandbox image not found. Run: sessions_refresh")
        return

    os.makedirs(session_path, exist_ok=True)
    workspace = os.path.join(session_path, "workspace")
    os.makedirs(workspace, exist_ok=True)

    print(f"[+] Created session: {name}")
    print("[*] Starting container...")

    if start_container_with_mount(session_path):
        write_current_session(name)
        print(f"[+] Session '{name}' ready.")
    else:
        print("[!] Failed to start container.")


def sessions_use(name: str):
    ensure_sessions_root()
    session_path = os.path.join(SESSIONS_DIR, name)

    if not os.path.exists(session_path):
        print(f"[!] Session '{name}' does not exist.")
        return

    if not docker_available():
        print("[!] Docker not available.")
        return

    if not image_exists():
        print("[!] Sandbox image missing. Run: sessions_refresh")
        return

    if container_running():
        stop_container()

    workspace = os.path.join(session_path, "workspace")
    os.makedirs(workspace, exist_ok=True)

    print(f"[*] Loading session '{name}'...")

    if start_container_with_mount(session_path):
        write_current_session(name)
        print(f"[+] Session '{name}' loaded.")
    else:
        print("[!] Failed to switch session.")


def sessions_delete(name: str):
    ensure_sessions_root()
    session_dir = os.path.join(SESSIONS_DIR, name)

    if not os.path.exists(session_dir):
        print(f"[!] Session '{name}' does not exist.")
        return

    shutil.rmtree(session_dir)
    print(f"[+] Deleted session: {name}")

    global CURRENT_SESSION
    if CURRENT_SESSION == name:
        CURRENT_SESSION = None
        if os.path.exists(CURRENT_FILE):
            os.remove(CURRENT_FILE)
        print("[*] Active session cleared.")


def sessions_nuke():
    ensure_sessions_root()

    stop_container()

    shutil.rmtree(SESSIONS_DIR)
    os.makedirs(SESSIONS_DIR)

    global CURRENT_SESSION
    CURRENT_SESSION = None

    print("[!] All sessions erased (image untouched).")


def sessions_shell():
    if not CURRENT_SESSION:
        print("[!] No active session.")
        return
    if not container_running():
        print("[!] Container is not running.")
        return
    subprocess.run(["docker", "exec", "-it", CONTAINER_NAME, "bash"])


def sessions_exec(command: str):
    if not CURRENT_SESSION:
        print("[!] No active session.")
        return
    if not container_running():
        print("[!] Container is not running.")
        return
    subprocess.run(["docker", "exec", "-it", CONTAINER_NAME, "bash", "-c", command])


def sessions_start():
    if not CURRENT_SESSION:
        print("[!] No active session.")
        return
    session_path = os.path.join(SESSIONS_DIR, CURRENT_SESSION)
    start_container_with_mount(session_path)


def sessions_stop():
    stop_container()


def sessions_ps():
    subprocess.run(["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}"])
