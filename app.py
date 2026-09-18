from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import os
import uuid

from werkzeug.utils import secure_filename
from flask_cors import CORS

from database import (
    save_chat,
    get_connection,
    list_sessions,
    clear_chat1,
    delete_session,
    list_archived_sessions,
    set_session_pinned,
    set_session_archived
)

from ollama_config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_STREAM
)

from mcp_client import search_document
from rag_service import ask_rag


# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIST = os.path.join(
    BASE_DIR,
    "frontend",
    "dist",
    "frontend",
    "browser"
)

print("Frontend:", FRONTEND_DIST)


# Create Flask app ONLY ONCE
app = Flask(
    __name__,
    static_folder=(
        FRONTEND_DIST
        if os.path.isdir(FRONTEND_DIST)
        else "static"
    )
)


# Enable CORS on the actual Flask app
CORS(app)

session_id = str(uuid.uuid4())

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Base directory of this file, used to locate the built Angular frontend.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist", "frontend", "browser")
print(FRONTEND_DIST)
# Serve static assets from the built Angular app when it exists, otherwise
# fall back to the legacy static/ folder. API endpoints are unaffected.
app = Flask(
    __name__,
    static_folder=FRONTEND_DIST if os.path.isdir(FRONTEND_DIST) else "static",
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

@app.route("/")
def home():
    # Serve the compiled Angular single-page app when available.
    
    if os.path.isdir(FRONTEND_DIST) and os.path.exists(
        os.path.join(FRONTEND_DIST, "index.html")
    ):
        return app.send_static_file("index.html")
    # Fallback to the original template when the frontend is not built.
    return render_template("index.html")

@app.route("/health-check")
def health():
    return "Healthy"

@app.route("/chat-stream", methods=["POST"])
def chat_stream():

    data = request.json

    messages = data["messages"]

    # Optional per-chat session id sent by the frontend "New chat" listener.
    # Falls back to the server-wide session id for older clients, so the
    # previous behaviour is fully preserved.
    active_session_id = data.get("session_id") or session_id

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

        save_chat(active_session_id, messages, full_reply)

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

@app.route("/pin_chat/<session_id>", methods=["POST"])
def pin_chat(session_id):
    set_session_pinned(session_id, 1)
    return jsonify({"success": True, "pinned": True})

@app.route("/unpin_chat/<session_id>", methods=["POST"])
def unpin_chat(session_id):
    set_session_pinned(session_id, 0)
    return jsonify({"success": True, "pinned": False})

@app.route("/archive_chat/<session_id>", methods=["POST"])
def archive_chat(session_id):
    set_session_archived(session_id, 1)
    return jsonify({"success": True, "archived": True})

@app.route("/unarchive_chat/<session_id>", methods=["POST"])
def unarchive_chat(session_id):
    set_session_archived(session_id, 0)
    return jsonify({"success": True, "archived": False})

@app.route("/archived-chats", methods=["GET"])
def get_archived_chats():
    return jsonify(list_archived_sessions())

@app.route("/upload-document", methods=["POST"])
def upload_document():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    filename = secure_filename(file.filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(file_path)

    return jsonify({
        "success": True,
        "message": "Document uploaded successfully",
        "filename": filename,
        "path": file_path
    })

@app.route("/ask-document", methods=["POST"])
def ask_document():

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({
            "success": False,
            "message": "Question is required"
        }), 400

    question = data["question"]

    # Document location
    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "tobacco.txt"
    )

    # Check whether document exists
    if not os.path.exists(file_path):
        return jsonify({
            "success": False,
            "message": "tobacco.txt has not been uploaded"
        }), 404

    # Read document
    with open(file_path, "r", encoding="utf-8") as file:
        document_text = file.read()

    # Prompt for Qwen
    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information
provided in the document below.

If the answer is not available in the document,
say: "The answer is not available in the uploaded document."

DOCUMENT:
--------------------
{document_text}
--------------------

USER QUESTION:
{question}

Give a clear and concise answer.
"""

    # Call Ollama
    ollama_response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:latest",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    if ollama_response.status_code != 200:
        return jsonify({
            "success": False,
            "message": "Ollama request failed",
            "details": ollama_response.text
        }), 500

    result = ollama_response.json()

    return jsonify({
        "success": True,
        "question": question,
        "answer": result.get("response", "")
    })

@app.route("/mcp-search", methods=["POST"])
def mcp_search():

    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({
            "success": False,
            "message": "Query is required"
        }), 400

    query = data["query"]

    try:

        result = search_document(query)

        return jsonify({
            "success": True,
            "query": query,
            "result": result
        })

    except Exception as exc:

        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500

@app.route("/ask-rag", methods=["POST"])
def ask_rag_api():

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({
            "success": False,
            "message": "Question is required"
        }), 400

    question = data["question"].strip()

    if not question:
        return jsonify({
            "success": False,
            "message": "Question cannot be empty"
        }), 400

    try:

        answer = ask_rag(question)

        return jsonify({
            "success": True,
            "question": question,
            "answer": answer
        })

    except Exception as exc:

        return jsonify({
            "success": False,
            "message": "RAG request failed",
            "details": str(exc)
        }), 500

@app.route("/cors-test", methods=["GET"])
def cors_test():
    return jsonify({
        "success": True,
        "message": "CORS is working"
    })


@app.route("/server-info", methods=["GET"])
def server_info():
    return jsonify({
        "server": "AI-Bot Flask",
        "message": "This is the correct Flask server"
    })

if __name__ == "__main__":
    app.run(debug=True)