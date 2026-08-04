"""Subprocess helper shared by verifiers that delegate to real tools.

Not a verifier, and not shared verifier-to-verifier state — every verifier
that imports this calls it independently, the same way any Python module
might use `subprocess` directly. This exists to avoid duplicating
timeout/error handling across Build and Test, not to couple them.

Platform note: contract commands (§5) are authored using POSIX shell
conventions — forward-slash relative paths, `&&` chaining — validated via
Git Bash. On native Windows, `subprocess.run(shell=True)` dispatches to
`cmd.exe`, which does not resolve those commands the way Git Bash does
(e.g. a leading `backend/.venv/Scripts/python.exe` is not found). Rather
than rewrite the contract-authoring convention, on Windows this module
explicitly locates and dispatches through Git Bash so the same command
text behaves identically on both platforms.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_GIT_BASH_CANDIDATES = (
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files (x86)\Git\bin\bash.exe",
)


@dataclass
class CommandResult:
    command: str
    returncode: int
    output: str


class GitBashNotFoundError(RuntimeError):
    """Raised when Windows command dispatch cannot locate a Git Bash executable."""


def _find_git_bash() -> str:
    found = shutil.which("bash")
    if found:
        return found
    for candidate in _GIT_BASH_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise GitBashNotFoundError(
        "Windows command dispatch requires Git Bash (bash.exe) to run contract "
        "commands with POSIX semantics, but none was found on PATH or in the "
        "usual Git-for-Windows install locations. Install Git for Windows, or "
        "ensure 'bash' is on PATH."
    )


def _build_popen_args(command: str) -> list[str] | str:
    if os.name == "nt" or sys.platform == "win32":
        bash = _find_git_bash()
        return [bash, "-c", command]
    return command


def run_command(command: str, cwd: Path, *, timeout: float = 300.0) -> CommandResult:
    try:
        popen_args = _build_popen_args(command)
    except GitBashNotFoundError as exc:
        return CommandResult(command=command, returncode=-1, output=str(exc))

    try:
        completed = subprocess.run(
            popen_args,
            cwd=cwd,
            shell=isinstance(popen_args, str),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        return CommandResult(command=command, returncode=completed.returncode, output=output)
    except subprocess.TimeoutExpired as exc:
        return CommandResult(command=command, returncode=-1, output=f"timed out after {timeout}s: {exc}")
    except OSError as exc:
        return CommandResult(command=command, returncode=-1, output=f"failed to execute: {exc}")
