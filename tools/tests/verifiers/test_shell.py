import sys
from pathlib import Path

import pytest

from fdk_verification.verifiers import _shell


def test_posix_dispatch_uses_shell_string(monkeypatch, tmp_path):
    monkeypatch.setattr(_shell, "os", type("os", (), {"name": "posix"}))
    monkeypatch.setattr(_shell.sys, "platform", "linux")

    result = _shell.run_command("echo hi", tmp_path)

    assert result.returncode == 0
    assert "hi" in result.output


def test_windows_dispatch_invokes_git_bash(monkeypatch, tmp_path):
    monkeypatch.setattr(_shell, "os", type("os", (), {"name": "nt"}))
    monkeypatch.setattr(_shell.sys, "platform", "win32")
    monkeypatch.setattr(_shell, "_find_git_bash", lambda: sys.executable)

    captured = {}

    def fake_run(popen_args, **kwargs):
        captured["popen_args"] = popen_args
        captured["shell"] = kwargs.get("shell")

        class _Completed:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Completed()

    monkeypatch.setattr(_shell.subprocess, "run", fake_run)

    result = _shell.run_command("echo hi", tmp_path)

    assert result.returncode == 0
    assert captured["shell"] is False
    assert captured["popen_args"] == [sys.executable, "-c", "echo hi"]


def test_windows_dispatch_fails_clearly_when_git_bash_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(_shell, "os", type("os", (), {"name": "nt"}))
    monkeypatch.setattr(_shell.sys, "platform", "win32")

    def raise_not_found():
        raise _shell.GitBashNotFoundError("no git bash here")

    monkeypatch.setattr(_shell, "_find_git_bash", raise_not_found)

    result = _shell.run_command("echo hi", tmp_path)

    assert result.returncode == -1
    assert "Git Bash" in result.output or "git bash" in result.output.lower()


def test_find_git_bash_raises_when_nothing_found(monkeypatch):
    monkeypatch.setattr(_shell.shutil, "which", lambda name: None)
    monkeypatch.setattr(_shell.Path, "is_file", lambda self: False)

    with pytest.raises(_shell.GitBashNotFoundError):
        _shell._find_git_bash()
