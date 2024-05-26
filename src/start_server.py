# A server with a backend and frontend that performs the following tasks:
# This is a chatbot server that receives a request from the client, sends the request to the backend, and receives the response from the backend.
# 1. Receives a request from the client
# 2. Sends the request to the backend
# 3. Receives the response from the backend

# Path: nexis/src/start_server.py

import threading


class Server(threading.Thread):
    def __init__(self, host, port, backend, frontend):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        self.backend = backend
        self.frontend = frontend

    def handle_request(self, request):
        response = self.backend.handle_request(request)
        return self.frontend.send_response(response)
    
    def run(self) -> None:
        return super().run()
