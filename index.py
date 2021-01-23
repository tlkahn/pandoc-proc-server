import re
import pypandoc
import os
from flask import Flask, request, Response, send_file, make_response
import gist
import hashlib
import threading

os.environ.setdefault('PYPANDOC_PANDOC', '/usr/bin/pandoc')

urls = (
    '/', 'index',
    '/fullpage', 'fullpage'
)


def clean(txt, href=''):
    def rm_line_breaks(match_obj):
        s1 = re.sub(r'[\n\r]+', '', match_obj.group(1))
        s2 = re.sub(r'[\n\r]+', '', match_obj.group(3))
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
        rm_patterns = [r'<<.*>>', r'\\\\', r'^\#\+BEGIN_HTML\n((?:.*\r?\n?)*)\#\+END_HTML']
        rp_patterns = [
            (r'\[\[(([^\]]|\n)+?)\]\[(([^\]]|\n)+?)\]\]', rm_line_breaks),
            (r'\n*\[\[(.+?)\]\[\]\]\s*=?(\w+)=?', r'[[\1][\2]]'),
            (r'[\u202F\u00A0]', ' '),
            (r'\[\[[^\]]+?\]\[\]\]', ''),
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
        for _, p in enumerate(rp_patterns):
            txt = re.sub(p[0], p[1], txt)

        return txt


def save_to_file(content, name='untitled.org', file_dir='./'):
    try:
        f = open(file_dir + name, "w")
        f.write(content)
    finally:
        f.close()


def expand_gist(match_obj):
    _id = match_obj.group(2)
    return '<pre>{}</pre>'.format(gist.get_content(_id))


def get_md5_checksum(input_str):

    return hashlib.md5(input_str.encode('utf-8')).hexdigest()


def get_domain(url):
    res = re.match(r'https?://([^/]+?)/.*', url).group(1)
    return res


def capture(input_str):
    input_str = re.sub(r'<div gistlink=\"https://gist.github.com/(.+?)/(.+?)\.js\">',
        expand_gist,
        input_str)
    # res = pypandoc.convert_text(input_str, 'latex', format='html', extra_args=['--wrap=none'])
    # t = threading.Thread(target=save_to_file, args = (res, 'output.tex', './'))
    # t.daemon = True
    # t.start()
    res = pypandoc.convert_text(
        input_str,
        'org',
        format='html-native_divs',
        extra_args=['--wrap=none'])
    # t = threading.Thread(target=save_to_file, args = (res, 'output.org', './'))
    # t.daemon = True
    # t.start()
    return res

def clear_screen():
    print('\033[2J')


def validate_sig(input_str, sig):
    return get_md5_checksum(input_str) == sig


def safe_str(s):
    try:
        return str(s)
    except UnicodeEncodeError:
        return s.encode('ascii', 'ignore').decode('ascii')
    return ""


app = Flask(__name__)


@app.route('/', methods=['POST'])
def home():
    if request.method == 'POST':
        html = request.form.get('html')
        sig = request.form.get('sig')
        href = request.form.get('url')
        clear_screen()
        print(html.encode('utf-8').decode('utf-8'))
        if validate_sig(href, sig):
            # file_name = 'untitled.org'
            # file_dir = './'
            result = clean(capture(html), href)
            # print('result: {}'.format(result))
            # save_to_file(result, file_name, file_dir)
            r = Response(response=result, status=200)
            r.headers['Access-Control-Allow-Origin'] = '*'
            r.headers['Access-Control-Allow-Credentials'] = 'true'
            r.headers['Content-Type'] = 'application/text; charset=utf-8'
            # response = make_response(send_file(file_full_path))
            # response.headers["Content-Disposition"] = \
            #     "attachment; " \
            #     "filename={};".format(file_full_path)
            return r
    else:
        return Response(response='ok', status=200)


app.run(host='0.0.0.0')
