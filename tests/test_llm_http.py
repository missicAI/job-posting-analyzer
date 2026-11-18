import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from joblens.llm import LLMClient, LLMError


@pytest.fixture
def server():
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            calls.append({"path": self.path, "payload": data})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            result = (
                {"message": {"content": '{"ok": true}'}}
                if self.path == "/api/chat"
                else {"choices": [{"message": {"content": '{"ok": true}'}}]}
            )
            self.wfile.write(json.dumps(result).encode())

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}", calls
    httpd.shutdown()
    httpd.server_close()
    thread.join()


@pytest.mark.parametrize("provider,path", [("ollama", "/api/chat"), ("compatible", "/v1/chat/completions")])
def test_real_http_serialization_for_both_protocols(server, provider, path):
    base, calls = server
    client = LLMClient(provider, base if provider == "ollama" else base + "/v1", "test-model")
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    assert json.loads(client.generate("system", "user", schema)) == {"ok": True}
    assert calls[0]["path"] == path
    sent = calls[0]["payload"]
    assert (
        sent["format"] == schema
        if provider == "ollama"
        else sent["response_format"]["json_schema"]["schema"] == schema
    )


def test_invalid_configuration_is_explicit():
    with pytest.raises(LLMError):
        LLMClient("unknown", "http://localhost", "test").generate("a", "b")
    with pytest.raises(LLMError):
        LLMClient("ollama", "file:///tmp/foo", "test").generate("a", "b")
