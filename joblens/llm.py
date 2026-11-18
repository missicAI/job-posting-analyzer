import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class LLMError(RuntimeError):
    pass


@dataclass
class LLMClient:
    provider: str
    base_url: str
    model: str
    api_key: str = ""
    timeout: float = 120

    @classmethod
    def from_env(cls):
        return cls(
            provider=os.getenv("LLM_PROVIDER", "ollama"),
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
            model=os.getenv("LLM_MODEL", "llama3.2:3b"),
            api_key=os.getenv("LLM_API_KEY", ""),
        )

    def generate(self, system: str, user: str, schema: dict | None = None) -> str:
        if self.provider not in {"ollama", "compatible"}:
            raise LLMError("LLM_PROVIDER phải là ollama hoặc compatible.")
        if urlparse(self.base_url).scheme not in {"http", "https"}:
            raise LLMError("LLM_BASE_URL phải bắt đầu bằng http:// hoặc https://.")
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        payload = {"model": self.model, "messages": messages, "stream": False}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.provider == "ollama":
            path = "/api/chat"
            payload["options"] = {"temperature": 0}
            if schema:
                payload["format"] = schema
        else:
            path = "/chat/completions"
            if schema:
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {"name": "result", "schema": schema},
                }
        request = Request(
            self.base_url.rstrip("/") + path,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except HTTPError as exc:
            raise LLMError(
                f"LLM trả HTTP {exc.code}. Kiểm tra tên mô hình, URL, khóa API "
                "và khả năng hỗ trợ JSON schema của nhà cung cấp."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise LLMError("Không kết nối được LLM. Kiểm tra máy chủ và thử lại.") from None
        except (ValueError, UnicodeError):
            raise LLMError("Máy chủ LLM trả dữ liệu không phải JSON hợp lệ.") from None
        try:
            content = (
                result["message"]["content"]
                if self.provider == "ollama"
                else result["choices"][0]["message"]["content"]
            )
        except (KeyError, IndexError, TypeError):
            raise LLMError("Phản hồi LLM thiếu nội dung trả lời.") from None
        if not isinstance(content, str) or not content.strip():
            raise LLMError("LLM không trả nội dung; có thể yêu cầu đã bị từ chối.")
        return content
