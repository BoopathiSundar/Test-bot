import subprocess
import sys

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Git Analysis Server")

@mcp.tool()
def git_status() -> str:
    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "status",
            "--short",
            "--branch"
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()

@mcp.tool()
def git_branches() -> str:
    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "branch",
            "-a"
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()

@mcp.tool()
def git_branches() -> str:
    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "branch",
            "-a"
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()


@mcp.tool()
def git_search(keyword: str) -> str:
    if not keyword.strip():
        return "Keyword cannot be empty."

    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "log",
            "--all",
            "--oneline",
            "--decorate",
            "--grep",
            keyword,
            "-i"
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip() or "No matching commits found."


@mcp.tool()
def git_file_history(
    filename: str,
    limit: int = 10
) -> str:

    if not filename.strip():
        return "Filename cannot be empty."

    limit = max(1, min(limit, 100))

    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "log",
            f"-{limit}",
            "--follow",
            "--date=short",
            "--pretty=format:%h | %ad | %an | %s",
            "--",
            filename
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip() or "No history found."


@mcp.tool()
def git_show_commit(commit: str) -> str:

    if not commit.strip():
        return "Commit cannot be empty."

    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "show",
            "--stat",
            "--oneline",
            commit
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()

@mcp.tool()
def git_diff() -> str:
    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "diff"
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip() or "No changes found."

@mcp.tool()
def git_log(limit: int = 5) -> str:
    result = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "git",
            "log",
            f"-{limit}",
            "--date=short",
            "--pretty=format:%h | %ad | %an | %s"
        ],
        cwd=r"D:\Boopathi\AI-Bot",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    if result.returncode != 0:
        return (
            f"Git command failed.\n"
            f"returncode: {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()

if __name__ == "__main__":
    mcp.run()