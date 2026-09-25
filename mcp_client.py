import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BASE_DIR = Path(__file__).resolve().parent

MCP_SERVER = (
    BASE_DIR
    / "mcp_servers"
    / "document_server.py"
    / "git_server.py"
)

async def call_git_mcp_tool(tool_name, arguments):

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER)],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):

            async with ClientSession(read, write) as session:

                print(f"Initializing MCP server: {GIT_MCP_SERVER}")

                await session.initialize()

                print(f"Calling tool: {tool_name}")

                result = await session.call_tool(
                    tool_name,
                    arguments
                )

                print("Tool call completed")

                output = []

                if result.content:
                    for item in result.content:
                        if hasattr(item, "text"):
                            output.append(item.text)
                        else:
                            output.append(str(item))

                return "\n".join(output)

    except BaseExceptionGroup as exc:

        print("\n===== MCP EXCEPTION GROUP =====")

        def print_exception(error, level=0):
            indent = "  " * level

            print(f"{indent}{type(error).__name__}: {error}")

            if isinstance(error, BaseExceptionGroup):
                for child in error.exceptions:
                    print_exception(child, level + 1)

        print_exception(exc)

        raise

    except Exception as exc:

        print("\n===== MCP ERROR =====")
        print(f"Type: {type(exc).__name__}")
        print(f"Message: {exc!r}")

        raise

def search_document(query):
    """
    Synchronous wrapper around the async MCP call.
    """

    return asyncio.run(
        call_git_mcp_tool(
            "search_document",
            {
                "query": query
            }
        )
    )


def list_documents():
    """
    List uploaded documents through MCP.
    """

    return asyncio.run(
        call_mcp_tool(
            "list_documents",
            {}
        )
    )


def read_document(filename):
    """
    Read a document through MCP.
    """

    return asyncio.run(
        call_mcp_tool(
            "read_document",
            {
                "filename": filename
            }
        )
    )

async def call_git_mcp_tool(tool_name, arguments):
    """
    Start the Git MCP server and execute a Git tool.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER)],
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

        def git_status():
         return asyncio.run(
         call_git_mcp_tool(
            "git_status",
            {}
        )
    )


def git_log(limit=10):
    return asyncio.run(
        call_git_mcp_tool(
            "git_log",
            {
                "limit": limit
            }
        )
    )


def git_diff():
    return asyncio.run(
        call_git_mcp_tool(
            "git_diff",
            {}
        )
    )


def git_branches():
    return asyncio.run(
        call_git_mcp_tool(
            "git_branches",
            {}
        )
    )


def git_search(keyword):
    return asyncio.run(
        call_git_mcp_tool(
            "git_search",
            {
                "keyword": keyword
            }
        )
    )


def git_file_history(filename, limit=10):
    return asyncio.run(
        call_git_mcp_tool(
            "git_file_history",
            {
                "filename": filename,
                "limit": limit
            }
        )
    )


def git_show_commit(commit):
    return asyncio.run(
        call_git_mcp_tool(
            "git_show_commit",
            {
                "commit": commit
            }
        )
    )