import requests
import json
from urllib.parse import urljoin
import time

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
            "messages": messages
        }
        # e.g. include temperature, max_tokens in kwargs
        payload.update(kwargs)
        return payload
    
    def unpackage(self, response):
        choices = response.get('choices', [])
        if choices:
            return choices[0].get('message', {}).get('content')
        return None


# --- OpenAI (official API) ---
class OpenAIRequest(ModelRequestMaker):
    def url_models(self, base_url):
        return urljoin(base_url, '/models')

    def url_chat(self, base_url):
        return urljoin(base_url, '/chat/completions')
    
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


# --- ModelProvider ---
class ModelProvider:
    def __init__(self, base_url, type=None, api_key=None, model=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.delta = -1
        self.response = None

        if type == 'ollama':
            self.req_maker = OllamaRequest()
        elif type == 'open-webui':
            self.req_maker = OpenWebUIRequest()
        elif type == 'openai':
            self.req_maker = OpenAIRequest()
        else:
            self.req_maker = None
        
        if self.req_maker:
            self.type = type
        else:
            raise ValueError(f"Unsupported MODEL_PROVIDER type: {type}")

    def _call(self, url, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            start = time.time()
            resp = requests.post(url, json=payload, headers=headers)
            self.delta = round(time.time() - start, 3)
            return resp
        except Exception as e:
            self.delta = -1
            raise RuntimeError(f"Request to {url} failed: {e}")

    def models(self):
        if not self.req_maker:
            raise RuntimeError("No request maker configured")
        url = self.req_maker.url_models(self.base_url)
        resp = self._call(url, None)
        return resp.json() if resp.status_code == 200 else resp.text

    def request(self, prompt, **kwargs):
        if not self.req_maker:
            return "!!ERROR!! No model provider configured"

        url = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kwargs)
        
        resp = self._call(url, payload)
        if resp.status_code == 200:
            data = resp.json()
            return self.req_maker.unpackage(data)
        elif resp.status_code == 401:
            return "!!ERROR!! Authentication failed (check your API key)"
        else:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"
