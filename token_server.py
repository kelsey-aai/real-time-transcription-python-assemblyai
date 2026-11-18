"""Mint a short-lived streaming token on your server, so browsers and apps never see your API key.

Run: python token_server.py   then GET http://localhost:8000/token
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from assemblyai.streaming.v3 import RealTimeTranscriber, RealTimeTranscriberOptions

client = RealTimeTranscriber(
    RealTimeTranscriberOptions(),
    api_key=os.environ["ASSEMBLYAI_API_KEY"],
)


class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/token":
            self.send_error(404)
            return
        # Add your own user authentication here before minting a token.
        token = client.create_temporary_token(
            expires_in_seconds=60,
            max_session_duration_seconds=3600,
        )
        body = json.dumps({"token": token}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("localhost", 8000), TokenHandler).serve_forever()
