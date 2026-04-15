#!/usr/bin/env python3

"""
ClaudePwn MCP server running INSIDE the Kali container.

Tools (all sandboxed under /workspace):

  - run_command(command, cwd=None, timeout=1200)
  - list_dir(path=".")
  - read_file(path, max_bytes=65536)
  - write_file(path, content, append=False)
  - tail_log(path, max_lines=200)
"""

import subprocess
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("ClaudePwn-Kali")
WORKSPACE_ROOT = Path("/workspace").resolve()


def _safe_path(rel_path: str) -> Path:
    """
    Resolve a path under /workspace and ensure it doesn't escape via .. tricks.
    """
    p = (WORKSPACE_ROOT / rel_path).resolve()
    if not str(p).startswith(str(WORKSPACE_ROOT)):
        raise ValueError("Path escapes /workspace")
    return p


# ---------------------------------------------------------------------------
# TOOL: run_command
# ---------------------------------------------------------------------------
@mcp.tool
def run_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 1200,
) -> dict:
    """
    Run a shell command inside the container (Kali).

    Args:
      command: Full shell command string, e.g. "nmap -sV 10.10.10.5"
      cwd: Optional path under /workspace to run in.
      timeout: Seconds before killing the process.
    """
    if cwd is not None:
        try:
            cwd_path = _safe_path(cwd)
        except ValueError as e:
            return {
                "error": str(e),
                "command": command,
                "cwd": cwd,
            }
    else:
        cwd_path = WORKSPACE_ROOT

    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd_path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": command,
            "cwd": str(cwd_path),
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-65536:],  # trim huge output
            "stderr": proc.stderr[-65536:],
        }
    except subprocess.TimeoutExpired as e:
        return {
            "command": command,
            "cwd": str(cwd_path),
            "error": f"Timeout after {timeout}s",
            "stdout": (e.stdout or "")[-65536:],
            "stderr": (e.stderr or "")[-65536:],
        }


# ---------------------------------------------------------------------------
# TOOL: list_dir
# ---------------------------------------------------------------------------
@mcp.tool
def list_dir(path: str = ".") -> dict:
    """
    List a directory under /workspace.
    """
    try:
        p = _safe_path(path)
    except ValueError as e:
        return {"error": str(e), "path": path}

    if not p.exists():
        return {"error": "Path does not exist", "path": str(p)}
    if not p.is_dir():
        return {"error": "Path is not a directory", "path": str(p)}

    entries = []
    for child in sorted(p.iterdir()):
        entries.append(
            {
                "name": child.name,
                "is_dir": child.is_dir(),
                "size": child.stat().st_size,
            }
        )

    return {"path": str(p), "entries": entries}


# ---------------------------------------------------------------------------
# TOOL: read_file
# ---------------------------------------------------------------------------
@mcp.tool
def read_file(path: str, max_bytes: int = 65536) -> dict:
    """
    Read a file under /workspace (truncated to max_bytes).
    """
    try:
        p = _safe_path(path)
    except ValueError as e:
        return {"error": str(e), "path": path}

    if not p.exists():
        return {"error": "File does not exist", "path": str(p)}
    if not p.is_file():
        return {"error": "Path is not a file", "path": str(p)}

    data = p.read_bytes()
    truncated = False
    if len(data) > max_bytes:
        data = data[-max_bytes:]
        truncated = True

    text = data.decode("utf-8", errors="replace")

    return {
        "path": str(p),
        "size": p.stat().st_size,
        "truncated": truncated,
        "content": text,
    }


# ---------------------------------------------------------------------------
# TOOL: write_file
# ---------------------------------------------------------------------------
@mcp.tool
def write_file(path: str, content: str, append: bool = False) -> dict:
    """
    Write or append text to a file under /workspace.
    """
    try:
        p = _safe_path(path)
    except ValueError as e:
        return {"error": str(e), "path": path}

    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with p.open(mode, encoding="utf-8") as f:
        f.write(content)

    return {
        "path": str(p),
        "size": p.stat().st_size,
        "append": append,
    }


# ---------------------------------------------------------------------------
# TOOL: tail_log
# ---------------------------------------------------------------------------
@mcp.tool
def tail_log(path: str, max_lines: int = 200) -> dict:
    """
    Tail the last N lines of a file under /workspace.
    Useful for reading long-running logs, e.g. /logs/enum_nmap.log
    """
    try:
        p = _safe_path(path)
    except ValueError as e:
        return {"error": str(e), "path": path}

    if not p.exists():
        return {"error": "File does not exist", "path": str(p)}
    if not p.is_file():
        return {"error": "Path is not a file", "path": str(p)}

    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return {"error": f"Failed to read file: {e}", "path": str(p)}

    if max_lines > 0:
        lines = lines[-max_lines:]

    return {"path": str(p), "lines": lines, "line_count": len(lines)}


# ---------------------------------------------------------------------------
# ENTRYPOINT: HTTP MCP at http://0.0.0.0:8000/mcp
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # transport="http" is the FastMCP way to expose an HTTP MCP endpoint
    # path="/mcp" is what Claude / FastMCPToolset expect by default
    # WARNING: Exposes remote command execution if publicly accessible - consider using 127.0.0.1
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
