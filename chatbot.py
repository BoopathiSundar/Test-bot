import sqlite3
import requests

from ollama_config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_STREAM

# Connect to SQLite
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

session_name = input("Enter session name: ")

cursor.execute(
    "INSERT INTO chat_session(session_name) VALUES(?)",
    (session_name,)
)

conn.commit()

session_id = cursor.lastrowid
print(session_id)

keyword = input("Search: ")

#cursor.execute("""
#SELECT user_message, bot_reply
#FROM chat_history
#WHERE user_message LIKE ?
#""", ('%' + keyword + '%',))

cursor.execute("""
    SELECT user_message, bot_reply, created_at
    FROM chat_history
    WHERE id = ?
    ORDER BY id
""", (keyword,))

rows = cursor.fetchall()
print(rows)
history = []

for user_msg, bot_msg, created_at in rows:
    history.append({
        "role": "user",
        "content": user_msg
    })

    history.append({
        "role": "assistant",
        "content": bot_msg
    })

for history in history:
    print(history["role"], ":", history["content"])

messages = []
while True:

    user_input = input("\nYou : ")

    if user_input.lower() == "exit":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": OLLAMA_STREAM,
        },
        timeout=OLLAMA_TIMEOUT,
    )

    if response.status_code == 200:

        bot_reply = response.json()["message"]["content"]

        print("\nBot :", bot_reply)

        messages.append({
            "role": "assistant",
            "content": bot_reply
        })

        # Save to SQLite
        cursor.execute(
            """
            INSERT INTO chat_history(session_id, role, user_message, bot_reply)
            VALUES (?, ?, ?, ?)
             """,
            (session_id, "user", user_input, "Bot session")
        )

        cursor.execute(
        """
         INSERT INTO chat_history(session_id, role, bot_reply, user_message)
            VALUES (?, ?, ?, ?)
             """,
            (session_id, "assistant", bot_reply, "Bot session")
        )

        conn.commit()

    else:
        print("Error:", response.text)

conn.close()