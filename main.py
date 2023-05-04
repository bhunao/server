import logging
from typing import Tuple
from markdown import markdown
from os import listdir
from os.path import isfile, join
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import http.server
import socketserver
from os import walk


logger = logging.getLogger(__name__)

PORT = 8000

notes_folder = 'C:\me\\notes'

def tag(tag: str):
    def return_func(*content, **keywords):
        keywords = " ".join([f'{key}="{value}"' for key, value in keywords.items()]) if keywords else ""
        tags = f'<{tag} {keywords if keywords else ""}>', f'</{tag}>'
        return tags[0] + '\n'.join(content)  + tags[1]
    return return_func

html_ = tag('html')
head = tag('head')
body = tag('body')
body = tag('body')
title = tag('title')
main = tag('main')
h1 = tag('h1')
div = tag('div')
link = tag('link')
script = tag('script')
button = tag('button')

def get_note(file_name):
    file_name = file_name + ".md"
    for dirpath, dirnames, filenames in walk(notes_folder):
        if file_name in filenames:
            file_path = join(dirpath, file_name)
            logger.debug(f'found file {file_path} in {dirpath}')
            try:
                with open(file_path, 'r') as file:
                    return markdown(file.read())
            except OSError:
                return http.HTTPStatus.NOT_FOUND


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        content = get_note(self.path[1:])

        status = HTTPStatus.OK if content else HTTPStatus.NOT_FOUND
        content = content if content else 'File not found'

        self.send_response(status)
        self.send_header('Content-type','text/html')
        self.end_headers()

        script_ = """
            int clicks = 0;
            function click() {
                clicks += 1;
                document.getElementById("clicks").innerHTML = clicks;
            };
            """
        button_tst = '<button type="button" onClick="click()">Click me</button>' + '<p>Clicks: <a id="clicks">0</a></p>'

        if status == HTTPStatus.OK:
            html = html_(
                head(
                    link(rel='stylesheet', href='https://cdn.simplecss.org/simple.min.css'
                         )
                ),
                body(
                    title(self.path),
                    div(content),
                    div(button_tst),
                    button("click me", type="button", onClick="click()"),
                    div("0", id="clicks"),
                    script(script_, type='text/javascript')
                )
            )

        else:
            html = html_(
                head(link(rel='stylesheet', href='https://cdn.simplecss.org/simple.min.css')),
                h1(content)
                )

        self.wfile.write(bytes(html, 'utf-8'))


        print(f'{self.path=}')
        return


with socketserver.TCPServer(("", PORT), Server) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()