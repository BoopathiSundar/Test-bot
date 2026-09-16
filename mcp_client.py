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
)


async def call_mcp_tool(tool_name, arguments):
    """
    Start the MCP document server, connect to it,
    and execute an MCP tool.
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


def search_document(query):
    """
    Synchronous wrapper around the async MCP call.
    """

    return asyncio.run(
        call_mcp_tool(
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