


<img src="docs/images/owlmind-banner.png" width=800>

### [Understand](./README.md) | [Get Started](./README.md#getting-started) | [Contribute](./CONTRIBUTING.md)
# Troubleshooting

## Issues with Python3 version compatibility

We tested with Python 3.11, 3.12, and above. 

Check your python version with:

```bash
$ python3 --version
Python 3.13.1
```

## Missing module **audioop**

This seems to be related to python3.13>. 

Importing this module has been included in requirements.txt. 

If it did not import correctly, you can make it run manually as:


```bash
python3 -m pip install --break-system-packages install audioop-lts
```

