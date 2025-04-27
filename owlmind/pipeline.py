import requests, time
from urllib.parse import urljoin

class ModelRequestMaker:
    def url_chat(self, base_url):
        raise NotImplementedError

    def package(self, model, prompt, **kw):
        raise NotImplementedError

    def unpackage(self, response):
        raise NotImplementedError

class OllamaRequest(ModelRequestMaker):
    def url_chat(self, base_url):
        return urljoin(base_url.rstrip('/'), '/api/generate')

    def package(self, model, prompt, **kw):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if kw:
            payload["options"] = kw
        return payload

    def unpackage(self, response):
        return response.get('response')

class ModelProvider:
    def __init__(self, base_url, model=None):
        self.base_url = base_url
        self.model    = model
        self.req_maker = OllamaRequest()

    def request(self, prompt, **kw):
        url     = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kw)
        headers = {"Content-Type": "application/json"}
        start   = time.time()
        resp    = requests.post(url, json=payload, headers=headers)
        self.delta = round(time.time() - start, 3)
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"
        return self.req_maker.unpackage(resp.json())
