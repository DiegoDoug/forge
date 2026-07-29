"""Git helper shared by verifiers that need "what changed" (Architecture,
Documentation, Code Quality). A generic utility, not a verifier and not
inter-verifier state.
"""

from __future__ import annotations

from pathlib import Path

from ._shell import run_command


def changed_files(workspace_root: Path) -> list[str]:
    """Paths (relative to workspace_root) with staged, unstaged, or untracked changes.

    Returns an empty list if workspace_root isn't a git repository, rather
    than raising — callers must treat that as "nothing to check against,"
    not as "confirmed nothing changed."
    """
    # -uall (--untracked-files=all): without it, git collapses an entirely
    # new, untracked directory into a single "?? dir/" line instead of
    # listing the files inside it — which would silently break any
    # verifier matching against individual file paths (Architecture,
    # Documentation, Code Quality).
    result = run_command("git status --porcelain -uall", workspace_root)
    if result.returncode != 0:
        return []

    files = []
    for line in result.output.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:  # rename: "old -> new"
            path = path.split(" -> ", 1)[1]
        files.append(path.strip('"'))
    return files
