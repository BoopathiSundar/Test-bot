import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MCP_SERVER = BASE_DIR / "mcp_servers" / "document_server.py"


# ---------------------------------------------------------
# Main test
# ---------------------------------------------------------

async def main():

    print("=" * 60)
    print("MCP DOCUMENT SERVER TEST")
    print("=" * 60)

    # Check MCP server file
    if not MCP_SERVER.exists():
        print(f"ERROR: MCP server not found:")
        print(MCP_SERVER)
        return

    print(f"MCP Server : {MCP_SERVER}")
    print()

    # MCP server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER)],
        env=None
    )

    print("Starting MCP server...")
    print()

    try:

        async with stdio_client(server_params) as (read, write):

            async with ClientSession(read, write) as session:

                # -------------------------------------------------
                # Initialize MCP connection
                # -------------------------------------------------

                print("Initializing MCP connection...")

                await session.initialize()

                print("MCP connection established.")
                print()

                # -------------------------------------------------
                # List available tools
                # -------------------------------------------------

                print("-" * 60)
                print("AVAILABLE MCP TOOLS")
                print("-" * 60)

                tools_result = await session.list_tools()

                for tool in tools_result.tools:

                    print(f"Tool : {tool.name}")

                    if tool.description:
                        print(f"Description : {tool.description}")

                    print()

                # -------------------------------------------------
                # Test list_documents()
                # -------------------------------------------------

                print("-" * 60)
                print("TEST 1: list_documents()")
                print("-" * 60)

                result = await session.call_tool(
                    "list_documents",
                    {}
                )

                print_result(result)

                # -------------------------------------------------
                # Test search_document()
                # -------------------------------------------------

                print("-" * 60)
                print("TEST 2: search_document('tobacco')")
                print("-" * 60)

                result = await session.call_tool(
                    "search_document",
                    {
                        "query": "tobacco"
                    }
                )

                print_result(result)

                # -------------------------------------------------
                # Test another search
                # -------------------------------------------------

                print("-" * 60)
                print("TEST 3: search_document('MPOWER')")
                print("-" * 60)

                result = await session.call_tool(
                    "search_document",
                    {
                        "query": "MPOWER"
                    }
                )

                print_result(result)

                print()
                print("=" * 60)
                print("MCP TEST COMPLETED")
                print("=" * 60)

                print("\nTEST 4: semantic_search_document('What is MPOWER?')")

                result = await session.call_tool(
                    "semantic_search_document",
                    {
                        "query": "What is MPOWER?",
                        "n_results": 3
                    }
                )

                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)

    except Exception as e:

        print()
        print("=" * 60)
        print("MCP TEST FAILED")
        print("=" * 60)

        print(f"Error: {e}")

        import traceback
        traceback.print_exc()


# ---------------------------------------------------------
# Print MCP result
# ---------------------------------------------------------

def print_result(result):

    if not result:
        print("No result returned.")
        return

    if hasattr(result, "isError") and result.isError:
        print("MCP TOOL ERROR")
        print()

    if hasattr(result, "content"):

        for item in result.content:

            if hasattr(item, "text"):
                print(item.text)

            else:
                print(item)

    else:
        print(result)


# ---------------------------------------------------------
# Start program
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())