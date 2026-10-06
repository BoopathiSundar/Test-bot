import asyncio
import sys
import os
import httpx
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client


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
# Jenkins MCP
# ============================================================

JENKINS_URL = os.getenv(
    "JENKINS_URL",
    "http://localhost:8080"
)

JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")

JENKINS_MCP_URL = f"{JENKINS_URL}/mcp-server/mcp"

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
# Jenkins MCP caller
# ============================================================

async def call_jenkins_tool(tool_name, arguments):
    """
    Connect to Jenkins MCP Server and execute a tool.
    """

    async with streamable_http_client(JENKINS_MCP_URL) as (
        read,
        write,
        _
    ):

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

def jenkins_get_status():
    return asyncio.run(
        call_jenkins_tool("getStatus", {})
    )


def jenkins_get_jobs():
    return asyncio.run(
        call_jenkins_tool("getJobs", {})
    )


def jenkins_get_job(job_full_name):
    return asyncio.run(
        call_jenkins_tool(
            "getJob",
            {
                "jobFullName": job_full_name
            }
        )
    )


def jenkins_get_build(job_full_name, build_number=None):
    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getBuild",
            arguments
        )
    )


def jenkins_get_build_log(
    job_full_name,
    build_number=None,
    limit=None
):
    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    if limit is not None:
        arguments["limit"] = limit

    return asyncio.run(
        call_jenkins_tool(
            "getBuildLog",
            arguments
        )
    )


def jenkins_search_build_log(
    job_full_name,
    pattern,
    build_number=None
):
    arguments = {
        "jobFullName": job_full_name,
        "pattern": pattern
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "searchBuildLog",
            arguments
        )
    )


def jenkins_get_test_results(
    job_full_name,
    build_number=None,
    only_failing_tests=False
):
    arguments = {
        "jobFullName": job_full_name,
        "onlyFailingTests": only_failing_tests
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getTestResults",
            arguments
        )
    )


def jenkins_get_build_scm(
    job_full_name,
    build_number=None
):
    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getBuildScm",
            arguments
        )
    )


def jenkins_get_build_changesets(
    job_full_name,
    build_number=None
):
    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getBuildChangeSets",
            arguments
        )
    )


def jenkins_get_job_scm(job_full_name):
    return asyncio.run(
        call_jenkins_tool(
            "getJobScm",
            {
                "jobFullName": job_full_name
            }
        )
    )


def jenkins_who_am_i():
    return asyncio.run(
        call_jenkins_tool(
            "whoAmI",
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

async def call_jenkins_tool(tool_name, arguments):
    """
    Connect to Jenkins MCP Server and execute a tool.
    """

    if not JENKINS_USER or not JENKINS_API_TOKEN:
        raise RuntimeError(
            "Jenkins credentials are not configured. "
            "Set JENKINS_USER and JENKINS_API_TOKEN."
        )

    http_client = httpx.AsyncClient(
        headers={
            "Authorization": (
                "Basic "
                + __import__("base64").b64encode(
                    f"{JENKINS_USER}:{JENKINS_API_TOKEN}".encode()
                ).decode()
            )
        },
        timeout=httpx.Timeout(
            30.0,
            read=300.0
        )
    )

    async with http_client:

        async with streamable_http_client(
            JENKINS_MCP_URL,
            http_client=http_client
        ) as (
            read,
            write,
            _
        ):

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

async def list_jenkins_tools():
    """
    List all tools exposed by Jenkins MCP Server.
    """

    if not JENKINS_USER or not JENKINS_API_TOKEN:
        raise RuntimeError(
            "Jenkins credentials are not configured."
        )

    import base64
    import httpx

    auth = base64.b64encode(
        f"{JENKINS_USER}:{JENKINS_API_TOKEN}".encode()
    ).decode()

    http_client = httpx.AsyncClient(
        headers={
            "Authorization": f"Basic {auth}"
        },
        timeout=httpx.Timeout(
            30.0,
            read=300.0
        )
    )

    async with http_client:

        async with streamable_http_client(
            JENKINS_MCP_URL,
            http_client=http_client
        ) as (
            read,
            write,
            _
        ):

            async with ClientSession(read, write) as session:

                await session.initialize()

                result = await session.list_tools()

                for tool in result.tools:

                    print("\n==============================")
                    print("TOOL:", tool.name)
                    print("==============================")
                    print("DESCRIPTION:")
                    print(tool.description)
                    print("INPUT SCHEMA:")
                    print(tool.inputSchema)

                return result.tools

def discover_jenkins_tools():
    return asyncio.run(
        list_jenkins_tools()
    )

# ============================================================
# Jenkins MCP tools
# ============================================================

def jenkins_get_jobs():
    return asyncio.run(
        call_jenkins_tool(
            "getJob",
            {
                "jobFullName": "sprint-boot-pipeline"
            }
        )
    )

# ============================================================
# Jenkins MCP tools
# ============================================================

def jenkins_get_status():
    """
    Get Jenkins controller health/status.
    """

    return asyncio.run(
        call_jenkins_tool(
            "getStatus",
            {}
        )
    )


def jenkins_get_jobs():
    """
    Get Jenkins jobs.
    """

    return asyncio.run(
        call_jenkins_tool(
            "getJobs",
            {}
        )
    )


def jenkins_get_job(job_full_name):
    """
    Get details of a Jenkins job.
    """

    return asyncio.run(
        call_jenkins_tool(
            "getJob",
            {
                "jobFullName": job_full_name
            }
        )
    )


def jenkins_get_build(job_full_name, build_number=None):
    """
    Get a specific Jenkins build.
    If build_number is omitted, gets the latest build.
    """

    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getBuild",
            arguments
        )
    )


def jenkins_get_build_log(
    job_full_name,
    build_number=None,
    limit=None
):
    """
    Get Jenkins build log.
    """

    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    if limit is not None:
        arguments["limit"] = limit

    return asyncio.run(
        call_jenkins_tool(
            "getBuildLog",
            arguments
        )
    )


def jenkins_search_build_log(
    job_full_name,
    pattern,
    build_number=None
):
    """
    Search Jenkins build logs.
    """

    arguments = {
        "jobFullName": job_full_name,
        "pattern": pattern
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "searchBuildLog",
            arguments
        )
    )


def jenkins_get_test_results(
    job_full_name,
    build_number=None,
    only_failing_tests=False
):
    """
    Get Jenkins test results.
    """

    arguments = {
        "jobFullName": job_full_name,
        "onlyFailingTests": only_failing_tests
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getTestResults",
            arguments
        )
    )


def jenkins_get_build_scm(
    job_full_name,
    build_number=None
):
    """
    Get SCM information for a Jenkins build.
    """

    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getBuildScm",
            arguments
        )
    )


def jenkins_get_build_changesets(
    job_full_name,
    build_number=None
):
    """
    Get change sets for a Jenkins build.
    """

    arguments = {
        "jobFullName": job_full_name
    }

    if build_number is not None:
        arguments["buildNumber"] = build_number

    return asyncio.run(
        call_jenkins_tool(
            "getBuildChangeSets",
            arguments
        )
    )


def jenkins_get_job_scm(job_full_name):
    """
    Get SCM configuration for a Jenkins job.
    """

    return asyncio.run(
        call_jenkins_tool(
            "getJobScm",
            {
                "jobFullName": job_full_name
            }
        )
    )


def jenkins_who_am_i():
    """
    Get the currently authenticated Jenkins user.
    """

    return asyncio.run(
        call_jenkins_tool(
            "whoAmI",
            {}
        )
    )

if __name__ == "__main__":

    print("\n===== JENKINS MCP TEST =====")

    try:

        print("\n===== JOB =====")
        print(
            jenkins_get_job(
                "sprint-boot-pipeline"
            )
        )

        print("\n===== LATEST BUILD =====")
        print(
            jenkins_get_build(
                "sprint-boot-pipeline"
            )
        )

        print("\n===== BUILD LOG =====")
        print(
            jenkins_get_build_log(
                "sprint-boot-pipeline",
                limit=30
            )
        )

        print("\n===== TEST RESULTS =====")
        print(
            jenkins_get_test_results(
                "sprint-boot-pipeline"
            )
        )

    except Exception as exc:

        import traceback

        print("\n===== JENKINS MCP ERROR =====")
        print(repr(exc))
        traceback.print_exc()