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
from mcp_client import (
    search_document,
    git_status,
    git_log,
    git_diff,
    git_branches,
    git_search,
    git_file_history,
    git_show_commit
)
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

def execute_git_tool(tool_name, arguments):
    """
    Execute an allowed Git MCP tool.
    """

    if tool_name == "git_status":
        return git_status()

    elif tool_name == "git_log":
        return git_log(
            arguments.get("limit", 10)
        )

    elif tool_name == "git_diff":
        return git_diff()

    elif tool_name == "git_branches":
        return git_branches()

    elif tool_name == "git_search":
        return git_search(
            arguments.get("keyword", "")
        )

    elif tool_name == "git_file_history":
        return git_file_history(
            arguments.get("filename", ""),
            arguments.get("limit", 10)
        )

    elif tool_name == "git_show_commit":
        return git_show_commit(
            arguments.get("commit", "")
        )

    else:
        raise ValueError(
            f"Unsupported Git MCP tool: {tool_name}"
        )

def ask_qwen_for_git_tool(question):

    prompt = f"""
You are a Git analysis assistant.

User question:
{question}

Determine whether the question requires information from the Git repository.

If Git information is NOT required, return ONLY:

{{
    "use_git": false
}}

If Git information IS required, select the most appropriate tool from the
following allowed Git tools.

Available tools:

1. git_status
   Use for questions about the current working tree status,
   modified files, staged files, or uncommitted changes.

2. git_log
   Use for questions about commits, recent commits, commit history,
   or latest commits.

3. git_diff
   Use for questions about current code changes or differences.

4. git_branches
   Use for questions about branches, available branches,
   current branches, or branch names.

5. git_search
   Use for searching the repository for a keyword or text.

6. git_file_history
   Use for questions about the history of a specific file.

7. git_show_commit
   Use when the user asks about a specific commit.

Return ONLY JSON.

Examples:

Question:
Show me the latest commits

Return:
{{
    "use_git": true,
    "tool": "git_log",
    "arguments": {{
        "limit": 10
    }}
}}

Question:
Show me the available branches

Return:
{{
    "use_git": true,
    "tool": "git_branches",
    "arguments": {{}}
}}

Question:
What files have been modified?

Return:
{{
    "use_git": true,
    "tool": "git_status",
    "arguments": {{}}
}}

Question:
Show me the changes

Return:
{{
    "use_git": true,
    "tool": "git_diff",
    "arguments": {{}}
}}

Question:
Show the history of app.py

Return:
{{
    "use_git": true,
    "tool": "git_file_history",
    "arguments": {{
        "filename": "app.py",
        "limit": 10
    }}
}}

Question:
Show commit 9d2f197

Return:
{{
    "use_git": true,
    "tool": "git_show_commit",
    "arguments": {{
        "commit": "9d2f197"
    }}
}}

Do not use markdown.
Do not add any explanation.
Return ONLY the JSON object.
"""

    print("\n===== QWEN GIT TOOL TEST =====")
    print("Question:", question)
    print("Model:", OLLAMA_MODEL)
    print("URL:", OLLAMA_URL)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        },
        timeout=OLLAMA_TIMEOUT
    )

    print("HTTP Status:", response.status_code)
    print("Raw Response:", response.text)

    response.raise_for_status()

    result = response.json()

    answer = result.get("message", {}).get("content", "")

    print("Qwen Answer:", repr(answer))

    return answer.strip()

@app.route("/git-ai-test", methods=["POST"])
def git_ai_test():

    try:
        data = request.get_json() or {}

        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "success": False,
                "error": "Question is required"
            }), 400

        decision = ask_qwen_for_git_tool(question)

        return jsonify({
            "success": True,
            "question": question,
            "decision": decision
        })

    except Exception as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

def parse_git_decision(decision_text):
    """
    Convert Qwen's Git decision into a Python dictionary.
    """

    try:
        decision = json.loads(decision_text)

        if not isinstance(decision, dict):
            return {
                "use_git": False
            }

        return decision

    except json.JSONDecodeError:

        print("Invalid Git decision from Qwen:")
        print(decision_text)

        return {
            "use_git": False
        }


import time

def get_git_context(question):

    start = time.time()

    print("\n===== GIT CONTEXT START =====")

    decision_start = time.time()

    decision_text = ask_qwen_for_git_tool(question)

    print(
        f"Qwen Git decision time: "
        f"{time.time() - decision_start:.2f} seconds"
    )

    decision = parse_git_decision(decision_text)

    print("\n===== GIT DECISION =====")
    print(decision)

    if not decision.get("use_git", False):

        print(
            f"Total Git context time: "
            f"{time.time() - start:.2f} seconds"
        )

        return {
            "used_git": False,
            "tool": None,
            "result": ""
        }

    tool_name = decision.get("tool")
    arguments = decision.get("arguments", {})

    if not tool_name:
        return {
            "used_git": False,
            "tool": None,
            "result": ""
        }

    print("\n===== EXECUTING GIT MCP =====")

    tool_start = time.time()

    try:

        result = execute_git_tool(
            tool_name,
            arguments
        )

        print(
            f"Git tool execution time: "
            f"{time.time() - tool_start:.2f} seconds"
        )

        print("\n===== GIT MCP RESULT =====")
        print(result)

        print(
            f"Total Git context time: "
            f"{time.time() - start:.2f} seconds"
        )

        return {
            "used_git": True,
            "tool": tool_name,
            "result": result
        }

    except Exception as exc:

        print("\n===== GIT MCP ERROR =====")
        print(str(exc))

        return {
            "used_git": False,
            "tool": tool_name,
            "result": "",
            "error": str(exc)
        }
    
@app.route("/git-context-test", methods=["POST"])
def git_context_test():

    try:

        data = request.get_json() or {}

        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "success": False,
                "error": "Question is required"
            }), 400

        git_context = get_git_context(question)

        return jsonify({
            "success": True,
            "question": question,
            "git_context": git_context
        })

    except Exception as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500
    
import time

@app.route("/chat-stream", methods=["POST"])
def chat_stream():

    data = request.json

    messages = data["messages"]

    # Optional per-chat session id sent by the frontend.
    # Falls back to the server-wide session id for older clients.
    active_session_id = data.get("session_id") or session_id

    # ---------------------------------------------------------
    # Get latest user message
    # ---------------------------------------------------------

    user_message = ""

    for message in reversed(messages):

        if message.get("role") == "user":

            user_message = message.get(
                "content",
                ""
            ).strip()

            break

    # ---------------------------------------------------------
    # Get Git context if required
    # ---------------------------------------------------------

    git_context = None

    if user_message:

        try:

            git_context = get_git_context(
                user_message
            )

            print(
                "\n===== CHAT STREAM GIT CONTEXT ====="
            )

            print(git_context)

        except Exception as exc:

            print(
                "\n===== GIT CONTEXT ERROR ====="
            )

            print(str(exc))

            git_context = None

    # ---------------------------------------------------------
    # Prepare messages for Ollama
    # ---------------------------------------------------------

    messages_for_ollama = messages.copy()

    if (
        git_context
        and git_context.get("used_git")
    ):

        git_result = git_context.get(
            "result",
            ""
        )

        if git_result:

            messages_for_ollama.append({

                "role": "system",

                "content": (
                    "The following information was "
                    "retrieved from the Git repository. "
                    "Use it to answer the user's question "
                    "accurately. "
                    "Do not invent Git information.\n\n"
                    "GIT CONTEXT:\n"
                    + str(git_result)
                )
            })

    # ---------------------------------------------------------
    # Stream response from Ollama
    # ---------------------------------------------------------

    def generate():

        full_reply = ""

        try:

            ollama_start = time.time()

            first_token = True

            print(
                "\n===== FINAL OLLAMA REQUEST ====="
            )

            print(
                "Starting Ollama request..."
            )

            response = requests.post(

                OLLAMA_URL,

                json={

                    "model": OLLAMA_MODEL,

                    "messages": messages_for_ollama,

                    "stream": OLLAMA_STREAM
                },

                stream=True,

                timeout=OLLAMA_TIMEOUT
            )

            response.raise_for_status()

            print(
                "Ollama HTTP response received in: "
                f"{time.time() - ollama_start:.2f} seconds"
            )

            # -------------------------------------------------
            # Read streaming response
            # -------------------------------------------------

            for line in response.iter_lines():

                if not line:
                    continue

                chunk = json.loads(line)

                # ---------------------------------------------
                # Ollama error
                # ---------------------------------------------

                if "error" in chunk:

                    yield (
                        f"\n[Error: "
                        f"{chunk['error']}]"
                    )

                    break

                # ---------------------------------------------
                # Normal response
                # ---------------------------------------------

                if "message" in chunk:

                    text = chunk["message"]["content"]

                    # Time to first token
                    if first_token:

                        print(
                            "Time to first token: "
                            f"{time.time() - ollama_start:.2f} seconds"
                        )

                        first_token = False

                    full_reply += text

                    yield text

            # -------------------------------------------------
            # Total Ollama time
            # -------------------------------------------------

            print(
                "Total Ollama streaming time: "
                f"{time.time() - ollama_start:.2f} seconds"
            )

        except requests.exceptions.ConnectionError:

            yield (
                "\n[Error: Could not connect to Ollama at "
                + OLLAMA_URL
                + ". Is the Ollama server running?]"
            )

        except requests.exceptions.Timeout:

            yield (
                "\n[Error: Ollama request timed out.]"
            )

        except Exception as exc:

            yield (
                f"\n[Error: {exc}]"
            )

        # -----------------------------------------------------
        # Save original chat messages
        # -----------------------------------------------------

        save_chat(
            active_session_id,
            messages,
            full_reply
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Return the streaming response
    # ---------------------------------------------------------

    return Response(
        generate(),
        mimetype="text/plain"
    )

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

    session_id = data.get("session_id")

    if not session_id:
        return jsonify({
            "success": False,
            "message": "session_id is required"
        }), 400

    try:
        # Search the document using RAG
        answer = ask_rag(question)

        # Save RAG conversation to SQLite
        save_chat(
            session_id,
            question,
            answer
        )

        print(f"RAG chat saved - session: {session_id}")

        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "session_id": session_id,
            "saved": True
        })

    except Exception as exc:

        print("RAG error:", exc)

        return jsonify({
            "success": False,
            "message": "RAG request failed",
            "details": str(exc)
        }), 500
    
@app.route("/server-info", methods=["GET"])
def server_info():
    return jsonify({
        "server": "AI-Bot Flask",
        "message": "This is the correct Flask server"
    })

@app.route("/git-mcp-test", methods=["POST"])
def git_mcp_test():

    try:
        data = request.get_json() or {}

        tool = data.get("tool", "git_status")

        if tool == "git_status":
            result = git_status()

        elif tool == "git_log":
            limit = data.get("limit", 10)
            result = git_log(limit)

        elif tool == "git_diff":
            result = git_diff()

        elif tool == "git_branches":
            result = git_branches()

        elif tool == "git_search":
            keyword = data.get("keyword", "")
            result = git_search(keyword)

        elif tool == "git_file_history":
            filename = data.get("filename", "")
            limit = data.get("limit", 10)
            result = git_file_history(filename, limit)

        elif tool == "git_show_commit":
            commit = data.get("commit", "")
            result = git_show_commit(commit)

        else:
            return jsonify({
                "success": False,
                "error": f"Unknown Git MCP tool: {tool}"
            }), 400

        return jsonify({
            "success": True,
            "tool": tool,
            "result": result
        })

    except Exception as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)