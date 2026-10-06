from app import ask_qwen_for_tool, parse_tool_decision


questions = [
    "Show me the latest commits",
    "Show my Jenkins jobs",
    "What is the status of sprint-boot-pipeline?",
    "Show build #4 details",
    "Show the build log",
    "What files have been modified?",
    "Explain what Docker is"
]


for question in questions:

    print("\n================================")
    print("QUESTION:", question)

    try:

        decision_text = ask_qwen_for_tool(question)

        decision = parse_tool_decision(
            decision_text
        )

        print("DECISION:")
        print(decision)

    except Exception as exc:

        print("ERROR:")
        print(repr(exc))