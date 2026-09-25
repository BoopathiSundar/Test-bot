import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BASE_DIR = Path(__file__).resolve().parent

SERVER_PATH = (
    BASE_DIR
    / "mcp_servers"
    / "git_server.py"
)


async def main():

    print("1 - FILE STARTED", flush=True)

    print("2 - ASYNCIO IMPORTED", flush=True)
    print("3 - SYS IMPORTED", flush=True)
    print("4 - PATH IMPORTED", flush=True)
    print("5 - MCP IMPORTED", flush=True)
    print("6 - STDIO IMPORTED", flush=True)

    print(
        f"7 - Server: {SERVER_PATH}",
        flush=True
    )

    print(
        f"8 - Exists: {SERVER_PATH.exists()}",
        flush=True
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            str(SERVER_PATH)
        ],
        env=None
    )

    print(
        "9 - Server parameters created",
        flush=True
    )

    print(
        f"10 - Python: {sys.executable}",
        flush=True
    )


async def test_git():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            str(SERVER_PATH)
        ],
        env=None
    )

    print(
        "11 - Entering main()",
        flush=True
    )

    async with stdio_client(server_params) as (
        read,
        write
    ):

        print(
            "12 - STDIO connected",
            flush=True
        )

        async with ClientSession(
            read,
            write
        ) as session:

            print(
                "13 - Initializing MCP...",
                flush=True
            )

            await session.initialize()

            print(
                "14 - MCP initialized",
                flush=True
            )

            # --------------------------------------
            # Git Branches
            # --------------------------------------

            print()
            print("15 - Calling git_branches...", flush=True)

            result = await session.call_tool(
                "git_branches",
                {}
            )

            print("16 - Tool returned", flush=True)
            print(result, flush=True)


            # --------------------------------------
            # Git Search
            # --------------------------------------

            print()
            print("17 - Calling git_search...", flush=True)

            result = await session.call_tool(
                "git_search",
                {
                    "keyword": "rag"
                }
            )

            print("18 - Tool returned", flush=True)
            print(result, flush=True)


            # --------------------------------------
            # Git File History
            # --------------------------------------

            print()
            print("19 - Calling git_file_history...", flush=True)

            result = await session.call_tool(
                "git_file_history",
                {
                    "filename": "mcp_servers/git_server.py",
                    "limit": 5
                }
            )

            print("20 - Tool returned", flush=True)
            print(result, flush=True)


            # --------------------------------------
            # Git Show Commit
            # --------------------------------------

            print()
            print("21 - Calling git_show_commit...", flush=True)

            result = await session.call_tool(
                "git_show_commit",
                {
                    "commit": "9d2f197"
                }
            )

            print("22 - Tool returned", flush=True)
            print(result, flush=True)

            print()
            print("23 - Calling git_diff...", flush=True)

            result = await session.call_tool(
                "git_diff",
                {}
            )

            print("24 - Tool returned", flush=True)
            print(result, flush=True)


if __name__ == "__main__":

    asyncio.run(test_git())