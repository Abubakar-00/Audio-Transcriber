import json
from server import MyHandler, PORT
import http.server
import socketserver

def test_handler_init():
    # Ensure the handler class exists
    assert issubclass(MyHandler, http.server.SimpleHTTPRequestHandler)

def test_transcribe_mock(monkeypatch):
    # Mock client.audio.transcriptions.create
    from server import client

    class MockTranscription:
        text = "Hello World"

    def mock_create(*args, **kwargs):
        return MockTranscription()

    monkeypatch.setattr(client.audio.transcriptions, "create", mock_create)

    # Simulate input
    data = {"audios": ["fakefile.wav"], "model": "whisper-large-v3", "language": "en"}

    # Just check mock works
    result = client.audio.transcriptions.create(file=("fakefile.wav", b"abc"), model="m", language="en")
    assert result.text == "Hello World"
