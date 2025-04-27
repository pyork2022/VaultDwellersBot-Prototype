# pipeline.py :: Pipeline for GenAI System (with debug logging)

import requests
import json
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
    def url_chat(self, base_url):
        return urljoin(base_url, '/api/generate')
    
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
        return response.get('response')


# --- OpenWebUI ---
class OpenWebUIRequest(ModelRequestMaker):
    def url_chat(self, base_url):
        return urljoin(base_url, '/api/chat/completions')
    
    def package(self, model, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        return payload
    
    def unpackage(self, response):
        choices = response.get('choices', [])
        if choices:
            return choices[0].get('message', {}).get('content')
        return None


# --- OpenAI (official API) ---
class OpenAIRequest(ModelRequestMaker):
    def url_models(self, base_url):
        return f"{base_url}/models"

    def url_chat(self, base_url):
        return f"{base_url}/chat/completions"
    
    def package(self, model, prompt, **kwargs):
        # conform to OpenAI chat endpoint
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        return payload
    
    def unpackage(self, response):
        choices = response.get('choices', [])
        if choices:
            return choices[0].get('message', {}).get('content')
        return None


# --- ModelProvider with debug prints ---
class ModelProvider:
    def __init__(self, base_url, type=None, api_key=None, model=None):
        self.base_url = base_url.rstrip('/')
        self.api_key   = api_key
        self.model     = model

        makers = {
            'ollama': OllamaRequest,
            'open-webui': OpenWebUIRequest,
            'openai': OpenAIRequest
        }
        if type not in makers:
            raise ValueError(f"Unsupported provider: {type}")
        self.req_maker = makers[type]()
        self.type = type
        self.delta = -1
        self.response = None

    def _call(self, url, payload):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # perform request
        resp = requests.post(url, json=payload, headers=headers)
        self.delta = round(time.time() - getattr(self, '_call_start', time.time()), 3)

        # debug: what URL and status we got back
        print(f"[AI DEBUG] ← {resp.status_code} from {resp.request.method} {resp.request.url}")
        return resp

    def models(self):
        url  = self.req_maker.url_models(self.base_url)
        print(f"[AI DEBUG] → GET models at: {url}")
        resp = self._call(url, None)
        return resp.json() if resp.status_code == 200 else resp.text

    def request(self, prompt, **kwargs):
        url     = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kwargs)

        # debug: show exactly what we're sending
        print(f"[AI DEBUG] → POST to: {url}")
        print(f"[AI DEBUG] → payload: {json.dumps(payload)}")

        resp = self._call(url, payload)
        if resp.status_code == 401:
            return "!!ERROR!! Authentication failed (check your API key)"
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"
        return self.req_maker.unpackage(resp.json())
