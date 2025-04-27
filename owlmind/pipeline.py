# owlmind/pipeline.py

import requests
import time
from urllib.parse import urljoin

# --- Request Maker Base ---
class ModelRequestMaker:
    def url_models(self, base_url):
        raise NotImplementedError("url_models() must be overridden")

    def url_chat(self, base_url):
        raise NotImplementedError("url_chat() must be overridden")
    
    def package(self, model, prompt, **kwargs):
        raise NotImplementedError("package() must be overridden")

    def unpackage(self, response):
        raise NotImplementedError("unpackage() must be overridden")


# --- Ollama ---
class OllamaRequest(ModelRequestMaker):
    def url_models(self, base_url):
        return urljoin(base_url, "/api/tags")

    def url_chat(self, base_url):
        return urljoin(base_url, "/api/generate")
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if kwargs:
            payload["options"] = kwargs
        return payload
    
    def unpackage(self, response):
        return response.get("response")


# --- OpenWebUI ---
class OpenWebUIRequest(ModelRequestMaker):
    def url_models(self, base_url):
        return urljoin(base_url, "/api/tags")

    def url_chat(self, base_url):
        return urljoin(base_url, "/api/chat/completions")
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        payload.update(kwargs)
        return payload
    
    def unpackage(self, response):
        choices = response.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content")
        return None


# --- OpenAI (official API) ---
class OpenAIRequest(ModelRequestMaker):
    def url_models(self, base_url):
        return urljoin(base_url, "/v1/models")

    def url_chat(self, base_url):
        return urljoin(base_url, "/v1/chat/completions")
    
    def package(self, model, prompt, **kwargs):
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
    
    def unpackage(self, response):
        choices = response.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content")
        return None


# --- ModelProvider ---
class ModelProvider:
    def __init__(self, base_url, type=None, api_key=None, model=None):
        """
        base_url: e.g. "https://api.openai.com" or "http://127.0.0.1:11434"
        type:     one of "ollama", "open-webui", "openai"
        api_key:  your bearer token (only needed for openai)
        model:    model name (e.g. "gpt-3.5-turbo" or "llama2")
        """
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.model    = model
        self.type     = type

        makers = {
            "ollama":     OllamaRequest,
            "open-webui": OpenWebUIRequest,
            "openai":     OpenAIRequest,
        }
        if self.type not in makers:
            raise ValueError(f"Unsupported provider type: {self.type!r}")
        self.req_maker = makers[self.type]()

    def _call(self, url, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        start = time.time()
        resp = requests.post(url, json=payload, headers=headers)
        self.delta = round(time.time() - start, 3)
        return resp

    def models(self):
        url  = self.req_maker.url_models(self.base_url)
        resp = self._call(url, None)
        if resp.status_code == 200:
            return resp.json()
        return resp.text

    def request(self, prompt, **kwargs):
        url     = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kwargs)
        resp    = self._call(url, payload)

        if resp.status_code == 401:
            return "!!ERROR!! Authentication failed"
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"
        return self.req_maker.unpackage(resp.json())
