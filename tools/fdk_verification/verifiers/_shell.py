"""Subprocess helper shared by verifiers that delegate to real tools.

Not a verifier, and not shared verifier-to-verifier state — every verifier
that imports this calls it independently, the same way any Python module
might use `subprocess` directly. This exists to avoid duplicating
timeout/error handling across Build and Test, not to couple them.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    command: str
    returncode: int
    output: str


def run_command(command: str, cwd: Path, *, timeout: float = 300.0) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
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
