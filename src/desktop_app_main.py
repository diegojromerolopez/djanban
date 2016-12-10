# -*- coding: utf-8 -*- 

import webview
import subprocess
import sys
import os
import cherrypy
import threading
import random
import string
import logging
import logging.handlers

# check if we are running as py2app bundle or as a script
if getattr(sys, 'frozen', None):
    base_dir = os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    run_as_binary = True
else:
    base_dir = os.path.realpath(os.path.dirname(__file__))
    run_as_binary = False

# set up logging and app_name
if run_as_binary is True:
    log_file = os.path.join(base_dir, "..", "DjangoTrelloStats.log")
    cherry_access_log = os.path.join(base_dir, "..", "access.log")
    cherry_error_log = os.path.join(base_dir, "..", "error.log")
    app_name = "PyBrowse"
else:
    log_file = os.path.join(base_dir, "DjangoTrelloStats.log")
    cherry_access_log = os.path.join(base_dir, "access.log")
    cherry_error_log = os.path.join(base_dir, "error.log")
    app_name = "Python"

log = logging.getLogger("DjangoTrelloStats")
log.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(log_file,
                                               maxBytes=30000000,
                                               backupCount=10)
handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(fmt)
log.addHandler(handler)

# make app show up as frontmost app
system_feedback = subprocess.Popen([
    "/usr/bin/osascript",
    "-e",
    'tell app \"Finder\" to set frontmost of process \"%s\" to true' % app_name],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    close_fds=True).communicate()[0].rstrip().decode("utf-8")


# create dynamic web server and let it run in the background.
class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return """<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<head>
    <title>PyBrowse</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="Description" content="MacDevOps:YVR 2016 test.">
    <link rel="stylesheet" type="text/css" media="screen" href="/static/css/style.css">
</head>

<body ondragstart="return false" draggable="false"
        ondragenter="event.dataTransfer.dropEffect='none'; event.stopPropagation(); event.preventDefault();"
        ondragover="event.dataTransfer.dropEffect='none';event.stopPropagation(); event.preventDefault();"
        ondrop="event.dataTransfer.dropEffect='none';event.stopPropagation(); event.preventDefault();">
<div class="welcome_string">Welcome to CherryPy powered by Python.</div>
<button type="button" onclick="get_data_from_backend()">Get data from server</button>
<div id="dynamic_block"></div>
<script>function get_data_from_backend() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("dynamic_block").innerHTML = xhttp.responseText;
      }
    };
    xhttp.open("GET", "generate", true);
    xhttp.send();
}
</script>
</body>
</html>"""

    @cherrypy.expose
    def generate(self):
        return ''.join(random.sample(string.hexdigits, 8))


def start_server():
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.config.update({'log.screen': False,
                            'log.access_file': cherry_access_log,
                            'log.error_file': cherry_error_log,
                            'server.socket_port': 9090}
                           )
    cherrypy.quickstart(HelloWorld(), "/", conf)


t = threading.Thread(target=start_server)
t.daemon = True
t.start()


# Create a resizable webview window with 800x600 dimensions 
webview.create_window("Django Trello Stats", "http://localhost:9090",
                      width=800, height=600, resizable=True, fullscreen=False)

