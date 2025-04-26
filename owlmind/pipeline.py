import requests
import json
from urllib.parse import urljoin
import time

class ModelRequestMaker:
    """
    Abstract interface for building model requests.
    """

    def url_models(self, url):
        raise NotImplementedError("url_models() must be implemented")

    def url_chat(self, url):
        raise NotImplementedError("url_chat() must be implemented")

    def package(self, model, prompt, **kwargs):
        raise NotImplementedError("package() must be implemented")

    def unpackage(self, response):
        raise NotImplementedError("unpackage() must be implemented")


class OllamaRequest(ModelRequestMaker):
    def url_chat(self, url):
        return urljoin(url, "/api/generate")

    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if kwargs:
            payload["options"] = {k: v for k, v in kwargs.items()}
        return payload

    def unpackage(self, response):
        return response.get("response", None)


class OpenWebUIRequest(ModelRequestMaker):
    def url_chat(self, url):
        return urljoin(url, "/api/chat/completions")

    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        # you can pass in OpenWebUI-specific kwargs here if needed
        return payload

    def unpackage(self, response):
        choices = response.get("choices")
        if choices and isinstance(choices, list):
            return choices[0].get("message", {}).get("content")
        return None


class OpenAIRequest(ModelRequestMaker):
    """
    Connects directly to OpenAI's /chat/completions endpoint using requests.
    """

    def url_chat(self, url):
        # expects base_url like "https://api.openai.com/v1"
        return urljoin(url, "/chat/completions")

    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        # pass through any other OpenAI parameters (temperature, max_tokens, etc.)
        payload.update(kwargs)
        return payload

    def unpackage(self, response):
        choices = response.get("choices")
        if choices and isinstance(choices, list):
            return choices[0].get("message", {}).get("content")
        return None


class ModelProvider:
    """
    Routes requests to the configured ModelRequestMaker.
    """

    def __init__(self, base_url, type=None, api_key=None, model=None):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.req_maker = None
        self.type = None
        self.delta = -1
        self.response = None

        if type == "ollama":
            self.req_maker = OllamaRequest()
            self.type = "ollama"
        elif type == "open-webui":
            self.req_maker = OpenWebUIRequest()
            self.type = "open-webui"
        elif type == "openai":
            self.req_maker = OpenAIRequest()
            self.type = "openai"
        # else: provider remains None

    def _call(self, url, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            start = time.time()
            resp = requests.post(url, headers=headers, data=json.dumps(payload) if payload else None)
            self.delta = round(time.time() - start, 3)
            return self.delta, resp
        except Exception as e:
            return -1, None

    def request(self, prompt, **kwargs):
        if not self.req_maker:
            return "!!ERROR!! No model provider configured."

        # build URL & payload
        url = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kwargs)

        # send and unpack
        delta, resp = self._call(url, payload)
        if resp is None:
            return f"!!ERROR!! Request to {url} failed."
        if resp.status_code == 401:
            return "!!ERROR!! Authentication failed – check your API key."
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"

        data = resp.json()
        return self.req_maker.unpackage(data)
