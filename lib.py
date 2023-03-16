import requests
import re
import uuid

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def concatList(s, l, c):
    for i in l:
        s += c + " " + i
    return s

def reformatPrompts(list):
    list = concatList('', re.findall("\d\..*\n", list + "\n"), '')
    return re.sub("\d\. ", "- ", list)

class GptCompletion:
    def __init__(self, api_key, org, model) -> None:
        self.api_key = api_key
        self.org = org
        self.model = model
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def complete(self, prompt, config={}):
        defaultConfig = {
            "model": self.model,
            "prompt": prompt
        }

        defaultConfig.update(config)
        res = requests.post('https://api.openai.com/v1/completions', 
            headers={
                'Authorization': 'Bearer ' + self.api_key,
                'OpenAI-Organization': self.org
            },
            json = defaultConfig
        ).json()
        if res.get('error') is not None:
            raise SyntaxError("error getting chat message: " + res.get('error').get('message'))
        self.prompt_tokens += res.get('usage').get('prompt_tokens')
        self.completion_tokens += res.get('usage').get('completion_tokens')
        self.total_tokens += res.get('usage').get('total_tokens')
        msg = res.get('choices')[0].get('text')
        return msg

class ImageCreation:
    def __init__(self, api_key, org):
        self.api_key = api_key
        self.org = org
    
    def create(self, prompt, config={}):
        defaultConfig = {
            "prompt": prompt
        }

        defaultConfig.update(config)
        res = requests.post('https://api.openai.com/v1/images/generations', 
            headers={
                'Authorization': 'Bearer ' + self.api_key,
                'OpenAI-Organization': self.org
            },
            json = defaultConfig
        ).json()
        if res.get('error') is not None:
            raise SyntaxError("error getting chat message: " + res.get('error').get('message'))
        msg = res.get('data')[0].get('url')
        return (res, msg)
    
    def download(self, path, prompt, config={}):
        (_, url) = self.create(prompt, config)
        name = str(uuid.uuid3(uuid.NAMESPACE_URL, url))
        img_data = requests.get(url).content
        with open(path + '/' + name + '.png', 'wb') as f:
            f.write(img_data)
        print('Image downloaded to: ' + name + '.png')