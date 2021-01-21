import web
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


def clean(txt, href=''):
    def rm_line_breaks(match_obj):
        s1 = re.sub(r'[\n\r]+', '', match_obj[1])
        s2 = re.sub(r'[\n\r]+', '', match_obj[3])
        res = '[[{}][{}]]'.format(s1, s2)
        return res

    def need_cleaning(_domain):
        if len(_domain) > 0 and _domain in ['www.bloomberg.com']:
            return True
        return False

    def update_patterns(_rm_patterns, _rp_patterns, _domain, _filters):
        rp = []
        rm = []
        if _domain in _filters:
            rp = _filters[_domain]['rp_patterns']
            rm = _filters[_domain]['rm_patterns']
        _rp_patterns += rp
        _rm_patterns += rm
        return _rm_patterns, _rp_patterns

    filters = {'www.bloomberg.com':
        {'rp_patterns': [
            (r'^\*([^\*\n]+?)\*$', r'\*\* \1'),
            (r'(?<!^)\n(?!(\n|$))', ''),
            (r'\[\[([^\]]+?)\]\[\]\](\n*)(\w+)', r'[[\1][\3]]'),
            (r'\[\[(([^\]]|\n)+?)\]\[(([^\]]|\n)+?)\]\]', rm_line_breaks),
            (r'\n', r'\n\n')
        ],
            'rm_patterns': []}
    }

    if len(href) > 0:
        domain = get_domain(href)
    else:
        domain = ''

    if len(txt) > 0:
        rm_patterns = [r'<<.*>>', r'\\\\']
        rp_patterns = [
            (r'\[\[(([^\]]|\n)+?)\]\[(([^\]]|\n)+?)\]\]', rm_line_breaks),
            (r'\n*\[\[(.+?)\]\[\]\]\s*=?(\w+)=?', r'[[\1][\2]]'),
            (r'[\u202F\u00A0]', ' '),
            (r'\s+(\#+CAPTION.+?)', r'\n\n\1'),
            (r'\s+(?=\n)', '\n'),
            (r'https:\/\/miro.medium.com\/max\/\d+', 'https://miro.medium.com/max/2048'),
            (':END:', r':END:\n\n'),
            (r'\n{2,}', r'\n\n'),
            ('、', '.'),
            (r'(\*?[一二三四五六七八九十]{1,}\W+.+?)', r'* \1')
        ]

        if need_cleaning(domain):
            rm_patterns, rp_patterns = update_patterns(rm_patterns, rp_patterns, domain, filters)

        for p in rm_patterns:
            txt = re.sub(p, r'', txt)
        for i, p in enumerate(rp_patterns):
            txt = re.sub(p[0], p[1], txt)

        save_to_file(txt)
        return txt


def save_to_file(content, name='untitled.org', dir='./'):
    try:
        f = open(dir+name, "a")
        f.write(content)
    except Exception as e:
        raise('error when writing to file', e)
    finally:
        f.close()


def expand_gist(match_obj):
    _id = match_obj.group(2)
    return '<pre>{}</pre>'.format(gist.get_content(_id))


def get_domain(url):
    res = re.match(r'https?://([^/]+?)/.*', url).group(1)
    return res


def capture(input_str):
    input_str = re.sub(r'<div gistlink=\"https://gist.github.com/(.+?)/(.+?)\.js\">', expand_gist, input_str)
    try:
        output = pypandoc.convert_text(input_str, 'org', format='html', extra_args=['--wrap=none'])
        res = output
    except:
        res = ''
    return res


class index:
    def POST(self):
        raw_input = web.data().decode('utf8')
        input_text = re.match(r'([^\n]+?)\n(.*)', raw_input)
        href = input_text.group(1)
        html = raw_input
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Content-Type', 'application/text')
        return clean(capture(html), href)


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
