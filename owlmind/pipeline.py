import requests, json, time
from urllib.parse import urljoin

class ModelRequestMaker:
    def url_models(self, base_url):         raise NotImplementedError
    def url_chat(self,   base_url):         raise NotImplementedError
    def package(self, model, prompt, **kw): raise NotImplementedError
    def unpackage(self, response):          raise NotImplementedError

class OllamaRequest(ModelRequestMaker):
    def url_chat(self, base_url):     return urljoin(base_url, '/api/generate')
    def package(self, model, prompt, **kw):
        p = {"model": model, "prompt": prompt, "stream": False}
        if kw: p["options"] = kw
        return p
    def unpackage(self, r): return r.get('response')

class OpenWebUIRequest(ModelRequestMaker):
    def url_chat(self, base_url):     return urljoin(base_url, '/api/chat/completions')
    def package(self, model, prompt, **kw):
        p = {"model": model, "messages": [{"role":"user","content":prompt}]}
        p.update(kw)
        return p
    def unpackage(self, r):
        ch = r.get('choices', [])
        return ch[0]['message']['content'] if ch else None

class OpenAIRequest(ModelRequestMaker):
    def url_models(self, base_url): return f"{base_url}/models"
    def url_chat(self,   base_url): return f"{base_url}/chat/completions"
    def package(self, model, prompt, **kw):
        return {"model": model,
                "messages": [{"role":"user","content":prompt}],
                **kw}
    def unpackage(self, response):
        ch = response.get('choices', [])
        return ch[0]['message']['content'] if ch else None

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

    def _call(self, url, payload):
        h = {"Content-Type":"application/json"}
        if self.api_key: h["Authorization"] = f"Bearer {self.api_key}"
        start = time.time()
        resp  = requests.post(url, json=payload, headers=h)
        self.delta = round(time.time()-start,3)
        return resp

    def models(self):
        url  = self.req_maker.url_models(self.base_url)
        resp = self._call(url, None)
        return resp.json() if resp.status_code==200 else resp.text

    def request(self, prompt, **kw):
        url     = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kw)
        resp    = self._call(url, payload)
        if resp.status_code == 401:
            return "!!ERROR!! Authentication failed"
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"
        return self.req_maker.unpackage(resp.json())
