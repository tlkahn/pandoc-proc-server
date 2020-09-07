import web
import json
import pypandoc
import os

os.environ.setdefault('PYPANDOC_PANDOC', '/usr/local/bin/pandoc')

urls = (
    '/', 'index',
)

class index:
    def POST(self):
        html = (web.data().decode('utf8'))
        # print(f"post successful with {params}")
        # param_dict = json.loads(params)
        # html = param_dict['html']
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        try:
            output = pypandoc.convert_text(html, 'org', format='html')
            res = output
        except:
            res = ''

        web.header('Content-Type', 'application/text')
        # return json.dumps(res)
        return res

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
