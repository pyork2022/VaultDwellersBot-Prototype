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
            payload["options"] = {key: value for key, value in kwargs.items()}
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
        return payload
    
    def unpackage(self, response):
        choices = response.get('choices', [])
        return choices[0]['message']['content'] if choices else None


class OpenAIRequest(ModelRequestMaker):
    """
    RequestMaker for OpenAI's REST API (v1).
    """
    def url_models(self, url):
        return urljoin(url, '/models')
    
    def url_chat(self, url):
        return urljoin(url, '/chat/completions')
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        # include any extra parameters (temperature, max_tokens, etc.)
        payload.update(kwargs)
        return payload
    
    def unpackage(self, response):
        choices = response.get('choices', [])
        return choices[0]['message']['content'] if choices else None


class ModelProvider:
    def __init__(self, base_url, type=None, api_key=None, model=None):
        self.base_url = base_url
        self.api_key = api_key
        self.type = None
        self.model = model
        self.req_maker = None
        self.delta = -1
        self.response = None

        # select appropriate request maker
        if type == 'ollama':
            self.req_maker = OllamaRequest()
            self.type = 'ollama'
        elif type == 'open-webui':
            self.req_maker = OpenWebUIRequest()
            self.type = 'open-webui'
        elif type == 'openai':
            self.req_maker = OpenAIRequest()
            self.type = 'openai'
        return

    def _call(self, url, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            start = time.time()
            response = requests.post(url, json=payload, headers=headers)
            self.delta = time.time() - start
        except Exception as e:
            return -1, None
        return self.delta, response

    def models(self):
        url = self.req_maker.url_models(self.base_url)
        return self._call(url)

    def request(self, prompt, **kwargs):
        # prepare payload
        url = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(model=self.model, prompt=prompt, **kwargs)

        # send HTTP request
        delta, response = self._call(url, payload)
        if not response:
            return "!!ERROR!! No response from API"
        if response.status_code == 401:
            return "!!ERROR!! Authentication issue. Check API_KEY"
        if response.status_code != 200:
            return f"!!ERROR!! HTTP {response.status_code}: {response.text}"

        data = response.json()
        return self.req_maker.unpackage(data)
