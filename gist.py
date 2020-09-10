import json
import requests

def get_content(gist_id):
   g = json.loads(requests.get(f'https://api.github.com/gists/{gist_id}', {'Accept': 'application/vnd.github.v3+json'}).text)
   return list(g['files'].values())[0]['content']

