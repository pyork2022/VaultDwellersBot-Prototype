import requests
import json
from urllib.parse import urljoin
import time

class ModelRequestMaker:
    def url_models(self, url):
        raise NotImplementedError("url_models() must be overridden")

    def url_chat(self, url):
        raise NotImplementedError("url_chat() must be overridden")
    
    def package(self, model, prompt, **kwargs):
        raise NotImplementedError("package() must be overridden")

    def unpackage(self, response):
        raise NotImplementedError("unpackage() must be overridden")


class OllamaRequest(ModelRequestMaker):
    def url_chat(self, url):
        return urljoin(url, '/api/generate')
    
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


class OpenWebUIRequest(ModelRequestMaker):
    def url_chat(self, url):
        return urljoin(url, '/api/chat/completions')
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        # you can pass temperature, top_p, etc. via kwargs
        payload.update(kwargs)
        return payload
    
    def unpackage(self, response):
        choices = response.get('choices', [])
        if choices:
            return choices[0]['message']['content']
        return None


class OpenAIRequest(ModelRequestMaker):
    def url_chat(self, url):
        # base_url should be "https://api.openai.com/v1"
        return f"{url.rstrip('/')}/chat/completions"
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        # pass through any OpenAI params (temperature, max_tokens, etc.)
        payload.update(kwargs)
        return payload

    def unpackage(self, response):
        choices = response.get('choices', [])
        if choices:
            return choices[0]['message']['content']
        return None


class ModelProvider:
    def __init__(self, base_url, type=None, api_key=None, model=None):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.delta = -1
        self.response = None

        # pick the correct request maker
        if type == 'ollama':
            self.req_maker = OllamaRequest()
            self.type = 'ollama'
        elif type == 'open-webui':
            self.req_maker = OpenWebUIRequest()
            self.type = 'open-webui'
        elif type == 'openai':
            self.req_maker = OpenAIRequest()
            self.type = 'openai'
        else:
            self.req_maker = None
            self.type = None

    def _call(self, url, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            start = time.time()
            resp = requests.post(url, json=payload, headers=headers)
            delta = time.time() - start
            return delta, resp
        except Exception as e:
            return -1, None

    def request(self, prompt, **kwargs):
        if not self.req_maker:
            return "!!ERROR!! No model provider configured."
        url = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(model=self.model, prompt=prompt, **kwargs)
        delta, resp = self._call(url, payload)

        if resp is None:
            return "!!ERROR!! Request failed. Check SERVER_URL and connectivity."
        if resp.status_code == 401:
            return "!!ERROR!! Authentication failed. Check your SERVER_API_KEY."
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"

        self.delta = round(delta, 3)
        self.response = resp.json()
        return self.req_maker.unpackage(self.response)
