from app import execute_api_tool


print("===== API TOOL TEST =====")

try:

    result = execute_api_tool(
        "get_sessions",
        {}
    )

    print("\nAPI TOOL RESULT:")
    print(result)

except Exception as exc:

    print("\nAPI TOOL ERROR:")
    print(repr(exc))