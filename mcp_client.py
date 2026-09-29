import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_MCP_SERVER = (
    BASE_DIR
    / "mcp_servers"
    / "document_server.py"
)

GIT_MCP_SERVER = (
    BASE_DIR
    / "mcp_servers"
    / "git_server.py"
)


# ============================================================
# Generic MCP caller
# ============================================================

async def call_mcp_tool(server_path, tool_name, arguments):
    """
    Start an MCP server and execute a tool.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=None
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            output = []

            if result.content:

                for item in result.content:

                    if hasattr(item, "text"):
                        output.append(item.text)

                    else:
                        output.append(str(item))

            return "\n".join(output)


# ============================================================
# Document MCP
# ============================================================

def search_document(query):
    """
    Search uploaded documents through Document MCP.
    """

    return asyncio.run(
        call_mcp_tool(
            DOCUMENT_MCP_SERVER,
            "search_document",
            {
                "query": query
            }
        )
    )


def list_documents():
    """
    List uploaded documents through Document MCP.
    """

    return asyncio.run(
        call_mcp_tool(
            DOCUMENT_MCP_SERVER,
            "list_documents",
            {}
        )
    )


def read_document(filename):
    """
    Read a document through Document MCP.
    """

    return asyncio.run(
        call_mcp_tool(
            DOCUMENT_MCP_SERVER,
            "read_document",
            {
                "filename": filename
            }
        )
    )


# ============================================================
# Git MCP
# ============================================================

def git_status():
    """
    Get current Git repository status.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_status",
            {}
        )
    )


def git_log(limit=10):
    """
    Get recent Git commits.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_log",
            {
                "limit": limit
            }
        )
    )


def git_diff():
    """
    Get current Git differences.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_diff",
            {}
        )
    )


def git_branches():
    """
    Get Git branches.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_branches",
            {}
        )
    )


def git_search(keyword):
    """
    Search Git commit history.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_search",
            {
                "keyword": keyword
            }
        )
    )


def git_file_history(filename, limit=10):
    """
    Get Git history for a specific file.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_file_history",
            {
                "filename": filename,
                "limit": limit
            }
        )
    )


def git_show_commit(commit):
    """
    Show details of a Git commit.
    """

    return asyncio.run(
        call_mcp_tool(
            GIT_MCP_SERVER,
            "git_show_commit",
            {
                "commit": commit
            }
        )
    )