# Basic HTTP Server (Socket API)

Simple HTTP-server, writen in Python using base module `socket`.

## Functions
- **Listens on port 8080** ip `127.0.0.1`('http://127.0.0.1:8080/').
- **Parse HTTP-requests**: gets method, path, query-parameters, headers and request body.
- **GET**:
  - `/` or `/index.html` — returns base HTML-page.
  - `/page?id=5` — processing query-parameters and shows ID.
  - any other - `404 Not Found`.
- **POST-**:
  - takes and parse `application/json` in request body.
  - returns JSON-response with confirmation of recieved data and headers.

## Server power on

To start the server do this command in bash:

```bash
py server.py

