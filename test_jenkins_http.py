import os
import base64
import httpx

JENKINS_URL = os.getenv(
    "JENKINS_URL",
    "http://localhost:8080"
)

JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")

url = f"{JENKINS_URL}/mcp-server/mcp"

auth = base64.b64encode(
    f"{JENKINS_USER}:{JENKINS_API_TOKEN}".encode()
).decode()

headers = {
    "Authorization": f"Basic {auth}",
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {
            "name": "ai-bot-test",
            "version": "1.0"
        }
    }
}

print("URL:", url)
print("User:", JENKINS_USER)
print("Sending initialize request...")

response = httpx.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

print("\nHTTP STATUS:")
print(response.status_code)

print("\nRESPONSE HEADERS:")
for key, value in response.headers.items():
    print(f"{key}: {value}")

print("\nRESPONSE BODY:")
print(response.text)