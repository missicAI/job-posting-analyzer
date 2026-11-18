from pathlib import Path
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest


def test_vietnamese_posting_and_reply(monkeypatch):
    import openai

    received = []

    class Client:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=self)

        def create(self, **kwargs):
            received.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Yêu cầu bắt buộc: Python. SQL là kỹ năng ưu tiên.")
                    )
                ]
            )

    monkeypatch.setattr(openai, "OpenAI", Client)
    at = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    at.chat_input[0].set_value("Tuyển thực tập sinh AI, yêu cầu Python, ưu tiên SQL.").run()
    assert not at.exception
    assert received[0]["messages"][-2]["content"].startswith("Tuyển thực tập")
    assert any("kỹ năng ưu tiên" in item.value for item in at.markdown)


def test_connection_error_is_shown_in_vietnamese(monkeypatch):
    import openai

    class Client:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=self)

        def create(self, **kwargs):
            raise ValueError("Không có phản hồi")

    monkeypatch.setattr(openai, "OpenAI", Client)
    at = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    at.chat_input[0].set_value("Đọc giúp tôi tin tuyển dụng này.").run()
    assert not at.exception
    assert "Chưa nhận được câu trả lời" in at.error[0].value
