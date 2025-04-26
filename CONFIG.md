
<img src="docs/images/owlmind-banner.png" width=800>

### [Understand](./README.md) | [Get Started](./README.md#getting-started) | [Contribute](./CONTRIBUTING.md)


# Connecting OwlMind to a Model Provider

* [General Audience](./CONFIG.md)
* [FAU Students](./CONFIG-FAU.md)

* Troubleshooting information at [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)


The configuration requires:
* The **Owlmind Framework** , which provides the simulated GenAI pipeline, and;
* Ollama Server as the server for GenAI models.

You have a few options for this configuration:

* (Option 1): Install both **Owlmind Framework** and **OLLAMA Server** on the same computer (RECOMMENDED)
* (Option 2): Install **Owlmind Framework** on one computer and use the **OLLAMA Server** installed on other computer in the same network (or accessible through the Internet, if feasible)


We recommend using [Visual Code Studio](https://code.visualstudio.com) and installing everything on your computer.

For both options, the installation steps include:
* (Step 1) Bringing up **Ollama Server**
* (Step 2) Downloading **Owlmind Framework** on your computer
* (Step 3) Connecting the **Owlmind Framework** with the **Ollama Server**
* (Step 4) Test the Environment


# (Step 1) Bringing up Ollama Server

Download and install OLLAMA following the instructions at:

[OLLAMA Download](https://ollama.com/download)

Detailed installation instructions at:

[OLLAMA Installation](https://github.com/ollama/ollama)

Once downloaded and installed, you can install GenAI models as:

```bash

ollama pull llama3.2

```

The list of models available are at:

[OLLAMA Model Library](https://ollama.com/library)

You can check the list of models installed in your computer as:


```bash

ollama ps

```

You can start OLLAMA Server to being able to access the models from the **Owlmind Framework** as:

```bash

ollama server

```

Note: if you install OLLAMA server on another computer, you need to make it listen to all network devices so you can access from the **Owlmind Framework** :


```bash
export OLLAMA_HOST=0.0.0.0
ollama server
```


At this point, OLLAMA is up and running and serving requests through port 11434.

> Note: If there is a `bind port error`  while initializing OLLAMA server, `check if the service is already running`, for instance:


```bash 
curl http://localhost:11434/api/ps
```



# (Step 2) Connecting the **Owlmind Framework** with the **Ollama Server**


Finally, you need to configure the environment so that the **Owlmind Framework** connected to your Model Server (Ollama).

You need to create the configuration file `.env` with the following parameters (a template is available; `just rename .env_example to .env`)


```bash

##
## EXAMPLE FOR .env file
## Rename this file to .env and complete the tokens
##

DISCORD_TOKEN=Your_Discord_Token
#SERVER_TYPE=ollama
#SERVER_URL=http://localhost:11434
SERVER_TYPE=open-webui
SERVER_URL=https://chat.hpc.fau.edu
SERVER_API_KEY=API_KEY_for_your_model_provider

```


# (Step 3) Test the Environment

Check if the Model Service is connecting.

```bash

python3 owlmind/pipeline.py

```

If it works


```bash

$ python3 owlmind/pipeline.py
P-> http://minipc:11434/api/generate {"model": "llama3.2", "prompt": "1+1", "stream": false}
1 + 1 = 2

```


