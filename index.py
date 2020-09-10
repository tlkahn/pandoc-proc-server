import web
import json
import pypandoc
import os
import requests
from readability import Document
import re
import pdb
import gist
os.environ.setdefault('PYPANDOC_PANDOC', '/usr/local/bin/pandoc')


urls = (
    '/', 'index',
    '/fullpage', 'fullpage'
)


def clean(txt):
    def rm_line_breaks(match_obj):
        s1 = re.sub(r'[\n\r]+', ' ', match_obj.group(1))
        s2 = re.sub(r'[\n\r]+', ' ', match_obj.group(3))
        res = f'[[{s1}][{s2}]]'
        return res

    if len(txt) > 0:
        rm_patterns = [r'<<.+?>>', r'\\\\']
        rp_patterns = [
            (r'\[\[(.+?)\]\[\]\]\s*(\w+)', r'[[\1][\2]]'),
            (r'^(\*+?)\s', r'\1* '),
            # (r'\[\[((.|\n)+?)\]\[((.|\n)+?)\]\]', rm_line_breaks),
            # (r'^\*([^\*\n]+?)\*$', '\*\* \1')
            (r'\n{2,}', r'\n\n'),
            # for bloomberg only
            # (r'(?<!^)\n(?!(\n|$))', ''),
            # (r'\n', r'\n\n')

        ]
        for p in rm_patterns:
            txt = re.sub(p, r'', txt)
        for i, p in enumerate(rp_patterns):
            txt = re.sub(p[0], p[1], txt)
        return txt
    else:
        return ''


def expand_gist(match_obj):
    id = match_obj.group(2)
    return f'<pre>{gist.get_content(id)}</pre>'


def capture(input):
    input = re.sub(r'<div gistlink=\"https:\/\/gist.github.com\/(.+?)\/(.+?)\.js\">', expand_gist, input)
    try:
        output = pypandoc.convert_text(input, 'org', format='html')
        res = output
    except:
        res = ''
    return res


class index:
    def POST(self):
        html = web.data().decode('utf8')
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Content-Type', 'application/text')
        return clean(capture(html))


class fullpage:
    def POST(self):
        url = web.data().decode('utf8')
        response = requests.get(url)
        doc = Document(response.text)
        summary = doc.summary()
        web.header('Content-Type', 'application/text')
        return clean(capture(summary))


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
