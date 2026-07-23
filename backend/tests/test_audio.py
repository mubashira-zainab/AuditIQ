from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_audio_text_endpoint_generates_speech():
    response = client.post(
        "/api/audio-text",
        data={
            "text": "Hello world from Audit IQ test suite.",
            "language": "English",
            "speed": 1.25,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 0
