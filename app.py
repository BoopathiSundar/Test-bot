from flask import Flask, render_template, request, jsonify, Response
import requests
import json, os
from database import save_chat, get_connection, list_sessions, clear_chat1, delete_session
import uuid
from ollama_config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_STREAM

session_id = str(uuid.uuid4())

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat-stream", methods=["POST"])
def chat_stream():

    data = request.json

    messages = data["messages"]

    def generate():
        full_reply = ""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": OLLAMA_STREAM
                },
                stream=True,
                timeout=OLLAMA_TIMEOUT
            )

            response.raise_for_status()

            for line in response.iter_lines():

                if not line:
                    continue

                chunk = json.loads(line)

                if "error" in chunk:
                    yield f"\n[Error: {chunk['error']}]"
                    break

                if "message" in chunk:
                    text = chunk["message"]["content"]

                    full_reply += text

                    yield text

        except requests.exceptions.ConnectionError:
            yield ("\n[Error: Could not connect to Ollama at "
                   + OLLAMA_URL + ". Is the Ollama server running?]")
        except requests.exceptions.Timeout:
            yield "\n[Error: Ollama request timed out.]"
        except Exception as exc:
            yield f"\n[Error: {exc}]"

        save_chat(session_id, messages, full_reply)

    return Response(generate(), mimetype="text/plain")

@app.route("/sessions", methods=["GET"])
def get_sessions():
    return jsonify(list_sessions())

@app.route("/clear-chat", methods=["DELETE"])
def clear_chat():
    print("clear - chart")
    return jsonify(clear_chat1())

@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_reply
        FROM chat_history
        WHERE session_id=?
        ORDER BY id
    """, (session_id,))

    rows = cursor.fetchall()

    messages = []

    for user, bot in rows:
        messages.append({
            "role": "user",
            "content": user
        })

        messages.append({
            "role": "assistant",
            "content": bot
        })

    messages.append({
        "role": "user",
        "content": user_message
    })

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": OLLAMA_STREAM
        },
        stream=True,
        timeout=OLLAMA_TIMEOUT
    )

    bot_reply = ""
    print(response)
    for line in response.iter_lines():

        if line:

            chunk = line.decode("utf-8")

            data = requests.models.complexjson.loads(chunk)

            print(data)
            bot_reply += data['message']['content']
    
    cursor.execute("""
        INSERT INTO chat_history
        (session_id,user_message,bot_reply)
        VALUES(?,?,?)
    """,(session_id,user_message,bot_reply))

    conn.commit()
    conn.close()

    return jsonify({
        "reply": bot_reply
    })

@app.route("/session/<session_id>")
def get_session(session_id):
    #print(os.path.abspath("chat.db"))
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_reply
        FROM chat_history
        WHERE session_id = ?
        ORDER BY id
    """, (session_id,))

    chats = cursor.fetchall()
    conn.close()

    return jsonify(chats)

@app.route("/delete_session/<session_id>", methods=["DELETE"])
def remove_session(session_id):

    delete_session(session_id)

    return {
        "success": True,
        "message": "Session deleted successfully"
    }

@app.route("/rename_session/<session_id>", methods=["PUT"])
def rename_session(session_id):

    data = request.json

    new_name = data.get("name")

    conn = get_connection()
    

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chat_session
        SET session_name = ?
        WHERE session_id = ?
    """, (new_name, session_id))

    conn.commit()

    return jsonify({
        "success": True
    })

if __name__ == "__main__":
    app.run(debug=True)