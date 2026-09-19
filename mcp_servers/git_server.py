import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Git Analysis Server")


# Change this to your actual Git repository
GIT_REPO = Path(r"D:\Boopathi\AI-Bot")


def run_git(*args):
    """
    Execute a Git command inside the repository.
    """

    result = subprocess.run(
        ["git", *args],
        cwd=GIT_REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


@mcp.tool()
def git_status():
    """
    Show the current Git branch and working-tree status.
    """

    branch = run_git(
        "branch",
        "--show-current"
    )

    status = run_git(
        "status",
        "--short"
    )

    return (
        f"Current branch: {branch or '(detached HEAD)'}\n\n"
        f"Working tree:\n{status or 'Clean'}"
    )


@mcp.tool()
def git_log(limit: int = 10):
    """
    Show recent Git commits.
    """

    return run_git(
        "log",
        f"-{limit}",
        "--date=short",
        "--pretty=format:%h | %ad | %an | %s"
    )


@mcp.tool()
def git_diff():
    """
    Show current uncommitted changes.
    """

    return run_git("diff")


@mcp.tool()
def git_branches():
    """
    Show local and remote Git branches.
    """

    return run_git(
        "branch",
        "-a"
    )


@mcp.tool()
def git_search(keyword: str):
    """
    Search Git commit history for a keyword.
    """

    return run_git(
        "log",
        "--all",
        "--oneline",
        "--decorate",
        "--grep",
        keyword,
        "-i"
    )


@mcp.tool()
def git_file_history(filename: str, limit: int = 10):
    """
    Show the commit history of a specific file.
    """

    return run_git(
        "log",
        f"-{limit}",
        "--follow",
        "--date=short",
        "--pretty=format:%h | %ad | %an | %s",
        "--",
        filename
    )


@mcp.tool()
def git_show_commit(commit: str):
    """
    Show details of a specific commit.
    """

    return run_git(
        "show",
        "--stat",
        "--oneline",
        commit
    )


if __name__ == "__main__":
    mcp.run()