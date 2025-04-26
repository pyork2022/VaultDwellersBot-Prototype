##
## OwlMind - Platform for Education and Experimentation with Hybrid Intelligent Systems
## pipeline.py :: Pipeline for GenAI System
## 
##
#  
# Copyright (c) 2024, The Generative Intelligence Lab @ FAU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# Documentation and Getting Started:
#    https://github.com/genilab-fau/owlmind
#
# Disclaimer: 
# Generative AI has been used extensively while developing this package.
# 

import requests
import json
from urllib.parse import urljoin
import time


class ModelRequestMaker():

    def url_models(self, url):
        raise(f'!!ERROR!! url_models() must be overload')

    def url_chat(self, url):
        raise(f'!!ERROR!! url_chat() must be overload')
    
    def package(self, prompt, model, **kwargs):
        raise(f'!!ERROR!! package() must be overload')

    def unpackage(self, response):
        raise(f'!!ERROR!! unpackage() must be overload')

class OllamaRequest(ModelRequestMaker):
    
    def url_chat(self, url):
        return urljoin(url, '/api/generate')
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model, 
            "prompt": prompt, 
            "stream": False,
        }

        # Load kwargs into payload.options
        if kwargs:
            payload["options"] = {key: value for key, value in kwargs.items()}
        return payload
    
    def unpackage(self, response):
        return response['response'] if 'response' in response else None


class OpenWebUIRequest(ModelRequestMaker):
    def url_chat(self, url):
        return urljoin(url, '/api/chat/completions')
    
    def package(self, model, prompt, **kwargs):
        payload = {
            "model": model if model else self.model, 
            "messages": [ {"role" : "user", "content": prompt } ]
        }

        # @NOTE: Need to find out the right syntax to load the arguments here!
        #kwargs = {key: value for key, value in self.__dict__}
        #if kwargs:
        #   payload["options"] = {key: value for key, value in kwargs.items()}
        return payload
    
    def unpackage(self, response):
        return response['choices'][0]['message']['content'] if 'choices' in response else None


###
### MODEL PROVIDER
### 

class ModelProvider():
    def __init__(self, base_url, type=None, api_key=None, model=None):
        self.base_url = base_url
        self.api_key = api_key
        self.type = None
        self.model = model
        self.req_maker = None
        self.delta = -1
        self.response = None


        if type == 'ollama':
            self.req_maker = OllamaRequest()
            self.type = 'ollama'
        elif type == 'open-webui':
            self.req_maker = OpenWebUIRequest()
            self.type = 'open-webui'
        return

    def _call(self, url, payload=None):
        """
        Issue the HTTP-Request to the Model Provider
        """
        headers = dict()
        headers["Content-Type"] = "application/json"
        if self.api_key: 
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            start_time = time.time()
            response = requests.post(url=url, data=payload, headers=headers)
            delta = time.time() - start_time
        except:
            return -1, f"!!ERROR!! Request failed! You need to adjust .env with URL({self.base_url})"
        
        return delta, response


    def models(self):
        """
        Issue request about Models Available
        """
        url = self.req_maker.url_models(base_url=self.url)
        return self._call(url=url)


    def request(self, prompt, **kwargs):
        """
        Execute the logic for request/response to a Model Provider.
        Creates the payload, issues the Request to the target Model provider.
        Unpackage the response, it any
        """

        ## (1) Creates the payload through the ModelRequestMaker
        url = self.req_maker.url_chat(self.base_url)
        payload = self.req_maker.package(model=self.model, prompt=prompt, **kwargs)
        payload = json.dumps(payload) if payload else None

        print('P->', url, payload)

        ## (2) Creates the HTTP-Req
        delta, response = self._call(url=url, payload=payload)

        # (3) Load the results
        if response is None:
            self.delta = -1
            self.response = None
            self.result = "!!ERROR!! There was no response (?)"
        elif isinstance(response,str):
            self.delta = -1
            self.response = None
            self.result = response
        elif response.status_code == 401:
            self.delta = -1
            self.response = None
            self.result = f"!!ERROR!! Authentication issue. You need to adjust .env with API_KEY ({self.base_url})"
        elif response.status_code == 200:
            self.delta = round(delta, 3)
            self.response = response.json()
            self.result = self.req_maker.unpackage(self.response)
        else: 
            self.delta = -1
            self.response = None
            self.result = f"!!ERROR!! HTTP Response={response.status_code}, {response.text}"
        
        return self.result 


##
## DEBUG
## TO BE DELETED

if __name__ == '__main__':
    from dotenv import dotenv_values

    # load token from .env
    config = dotenv_values('.env')
    URL = config['SERVER_URL']
    MODEL = config['SERVER_MODEL'] if 'SERVER_MODEL' in config else None
    TYPE = config['SERVER_TYPE'] if 'SERVER_TYPE' in config else None
    API_KEY = config['SERVER_API_KEY'] if 'SERVER_API_KEY' in config else None

    # Configure a ModelProvider if there is an URL
    provider = ModelProvider(type=TYPE,  base_url=URL, api_key=API_KEY, model=MODEL) if URL else None
    print(provider.request(prompt="1+1"))

