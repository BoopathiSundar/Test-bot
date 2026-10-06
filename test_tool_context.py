from app import execute_api_tool


result = execute_api_tool(
    "get_sessions",
    {}
)

print("\n===== API TOOL RESULT =====")
print(result)