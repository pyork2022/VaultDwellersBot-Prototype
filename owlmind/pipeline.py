import requests
import time
from urllib.parse import urljoin


class ModelRequestMaker:
    def url_models(self, base_url: str) -> str:
        raise NotImplementedError

    def url_chat(self, base_url: str) -> str:
        raise NotImplementedError

    def package(self, model: str, prompt: str, **kwargs) -> dict:
        raise NotImplementedError

    def unpackage(self, response: dict) -> str:
        raise NotImplementedError


class OllamaRequest(ModelRequestMaker):
    def url_chat(self, base_url: str) -> str:
        return urljoin(base_url.rstrip('/'), '/api/generate')

    def package(self, model: str, prompt: str, **kwargs) -> dict:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if kwargs:
            payload["options"] = kwargs
        return payload

    def unpackage(self, response: dict) -> str:
        return response.get('response', None)


class OpenWebUIRequest(ModelRequestMaker):
    def url_chat(self, base_url: str) -> str:
        return urljoin(base_url.rstrip('/'), '/api/chat/completions')

    def package(self, model: str, prompt: str, **kwargs) -> dict:
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }

    def unpackage(self, response: dict) -> str:
        choices = response.get('choices', [])
        if choices:
            return choices[0].get('message', {}).get('content')
        return None


class OpenAIRequest(ModelRequestMaker):
    def url_models(self, base_url: str) -> str:
        return urljoin(base_url.rstrip('/'), '/models')

    def url_chat(self, base_url: str) -> str:
        return urljoin(base_url.rstrip('/'), '/chat/completions')

    def package(self, model: str, prompt: str, **kwargs) -> dict:
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }

    def unpackage(self, response: dict) -> str:
        choices = response.get('choices', [])
        if choices:
            return choices[0].get('message', {}).get('content')
        return None


class ModelProvider:
    def __init__(self, base_url: str, type: str = None, api_key: str = None, model: str = None):
        self.base_url = base_url
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
            raise ValueError(f"Unsupported MODEL_PROVIDER type: {type}")

    def _call(self, url: str, payload: dict = None) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        start = time.time()
        resp = requests.post(url, json=payload, headers=headers)
        self.delta = round(time.time() - start, 3)
        return resp

    def models(self):
        url = self.req_maker.url_models(self.base_url)
        resp = self._call(url)
        return resp.json() if resp.status_code == 200 else resp.text

    def request(self, prompt: str, **kwargs) -> str:
        url = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(self.model, prompt, **kwargs)
        resp = self._call(url, payload)

        if resp.status_code == 200:
            data = resp.json()
            return self.req_maker.unpackage(data)
        if resp.status_code == 401:
            return "!!ERROR!! Authentication failed (check your API key)"
        return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"


# --- DEBUG / quick test ---
if __name__ == '__main__':
    from dotenv import dotenv_values
    cfg = dotenv_values('.env')
    prov = ModelProvider(
        base_url=cfg['SERVER_URL'],
        type=cfg['SERVER_TYPE'],
        api_key=cfg['SERVER_API_KEY'],
        model=cfg['SERVER_MODEL']
    )
    print(prov.request("1+1"))
