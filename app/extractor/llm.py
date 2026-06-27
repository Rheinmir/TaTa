"""LLM client — interface + 2 impl.

- FakeLLM: trả JSON cố định theo hàm responder (test offline, không gọi mạng).
- AzureLiteLLMClient: gọi OpenAI-compatible /chat/completions (LiteLLM proxy hoặc
  Azure model-inference). Cấu hình qua env:
    TATA_LLM_BASE_URL   (vd http://localhost:4000  của LiteLLM, hoặc Azure endpoint)
    TATA_LLM_API_KEY
    TATA_EXTRACT_MODEL  (mặc định gpt-4.1-mini)
    TATA_LLM_FLAVOR     openai (mặc định, header Bearer) | azure (header api-key + api-version)
    AZURE_API_VERSION
"""
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Extractor.LLM")


class LLMClient:
    def complete(self, system, user):
        """Trả chuỗi text (kỳ vọng JSON) từ model."""
        raise NotImplementedError


class FakeLLM(LLMClient):
    def __init__(self, responder):
        # responder(system, user) -> str (JSON)
        self.responder = responder

    def complete(self, system, user):
        return self.responder(system, user)


class AzureLiteLLMClient(LLMClient):
    def __init__(self, base_url=None, api_key=None, model=None, flavor=None, api_version=None, session=None):
        self.base_url = (base_url or os.environ.get("TATA_LLM_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.environ.get("TATA_LLM_API_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
        self.model = model or os.environ.get("TATA_EXTRACT_MODEL", "gpt-4.1-mini")
        self.flavor = flavor or os.environ.get("TATA_LLM_FLAVOR", "openai")
        self.api_version = api_version or os.environ.get("AZURE_API_VERSION", "2024-05-01-preview")
        import requests
        self._s = session or requests.Session()

    @property
    def configured(self):
        return bool(self.base_url and self.api_key)

    def complete(self, system, user):
        if not self.configured:
            raise RuntimeError("LLM chưa cấu hình (TATA_LLM_BASE_URL/API_KEY).")
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        if self.flavor == "azure":
            url = f"{self.base_url}/chat/completions?api-version={self.api_version}"
            headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        else:
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        r = self._s.post(url, headers=headers, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


def parse_tasks(raw):
    """Bóc JSON từ output model (bỏ rào ```), trả list tasks (rỗng nếu lỗi)."""
    if not raw:
        return []
    s = raw.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s[:4].lower() == "json":
            s = s[4:]
    s = s.strip()
    try:
        obj = json.loads(s)
    except Exception:  # noqa: BLE001
        # thử tìm khối {...} đầu tiên
        i, j = s.find("{"), s.rfind("}")
        if i >= 0 and j > i:
            try:
                obj = json.loads(s[i:j + 1])
            except Exception:  # noqa: BLE001
                return []
        else:
            return []
    tasks = obj.get("tasks") if isinstance(obj, dict) else obj
    return tasks if isinstance(tasks, list) else []
