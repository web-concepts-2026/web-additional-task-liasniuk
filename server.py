import json
import os
import socket
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8080

def parse_request(request):
    parts = request.split("\r\n\r\n", 1)
    header = parts[0]
    if(len(parts)>1):
        body = parts[1]
    else:
        body = ""

    lines = header.split("\r\n")
    if not lines or not lines[0]:
        return None

    request = lines[0].split(" ")
    method = request[0]
    full_path = request[1] if len(request)>1 else "/"

    url = urlparse(full_path)
    path = url.path
    query = parse_qs(url.query)

    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    return {
        "method": method,
        "path": path,
        "query_params": query,
        "headers": headers,
        "body": body,
    }

def build_response(status_code, status_text, content_type, body):
    response_body = (json.dumps(body) if isinstance(body, dict) else body).encode("utf-8")
    headers = [
        f"HTTP/1.1 {status_code} {status_text}",
        f"Content-Type: {content_type}; charset=utf-8",
        f"Content-Length: {len(response_body)}",
        "Connection: close",
        "",
        "",
    ]

    return "\r\n".join(headers).encode("utf-8") + response_body

def handle_client(client_socket):
    raw_data = client_socket.recv(4096).decode("utf-8", errors="ignore")
    if not raw_data:
        client_socket.close()
        return
    request = parse_request(raw_data)
    if not request:
        client_socket.close()
        return

    method = request["method"]
    path = request["path"]

    if method=="GET":
        if path == "/" or path == "/index.html":
            html_content = (
                "<html><body><h1>Server Works!</h1></body></html>"
            )
            response = build_response(200, "OK", "text/html", html_content)
        elif path == "/page":
            user_id = request["query_params"].get("id", ["N/A"])[0]
            html_content = (
                f"<html><body><h1>Page ID: {user_id}</h1></body></html>"
            )
            response = build_response(200, "OK", "text/html", html_content)
        else:
            response = build_response(
                404, "Not Found", "text/html", "<h1>404 Not Found</h1>"
            )
    elif method=="POST":
        try:
            json_body = json.loads(request["body"]) if request["body"] else {}
            res_data = {
                "message": "Data received successfully!",
                "received_data": json_body,
                "headers_received": request["headers"],
            }
            response = build_response(
                200, "OK", "application/json", res_data
            )
        except json.JSONDecodeError:
            response = build_response(
                400,
                "Bad Request",
                "application/json",
                {"error": "Invalid JSON"},
            )
    else:
        response = build_response(405, "Method not provided", "text/plain", "Method Not Allowed")

    client_socket.sendall(response)
    client_socket.close()

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Server listening on http://{HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()