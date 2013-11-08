# -*- coding:utf-8 -*-

from thememapper.core.controller.server import _ServerController
from flask import Flask, g, request
from flask.ext.babel import Babel, gettext
from werkzeug.routing import BaseConverter
import os
import argparse

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = Flask(__name__)
app.threaded = True
app.url_map.converters['regex'] = RegexConverter

# Babel (i18n)
babel = Babel(app)
_ = gettext

# Babel
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'

# Available languages
AVAILABLE_LOCALES = ['en', 'es']

@babel.localeselector
def get_locale():
    # Try to guess the language from the user accept
    # header the browser transmits.  We support es/en in this
    # moment.  The best match wins.
    return request.accept_languages.best_match(AVAILABLE_LOCALES)

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

def start_thememapper():
    global settings
    # Adds the ability to set config file and port through commandline
    p = argparse.ArgumentParser(description='Configure thememapper.core')
    p.add_argument('--port', default=None,help='port thememapper should run at')
    p.add_argument('--diazo', default=False,action="store_true",dest="diazo",help='force diazo server to run')
    p.add_argument('--diazo_port', default=None,help='port diazo should run at')
    p.add_argument('--static_path', default=None,help='path to static folder')
    args =  p.parse_args()
    server = _ServerController(app,args)
    settings = server.settings
    server.watch(os.path.join(os.path.dirname(__file__), 'settings.properties'))
    server.start()

@app.route("/")
def index():
    from thememapper.core.controller.dashboard import _DashboardController
    dashboard = _DashboardController(settings)
    return dashboard.show_dashboard()

@app.route("/editor/", methods=["GET", "POST"])
@app.route("/editor/<name>/", methods=["GET", "POST"])
@app.route('/editor/<name>/<regex("(.*)"):path>')
def editor(name=None,path=None):
    from thememapper.core.controller.editor import _EditorController
    editor = _EditorController(settings)
    if name == 'result':
        return editor.show_result(path)
    else:
        return editor.show_editor(name)

@app.route("/settings/", methods=["GET", "POST"])
@app.route("/settings/<name>/", methods=["GET", "POST"])
def settings(name=None):
    from thememapper.core.controller.settings import _SettingsController
    settings = _SettingsController()
    if name is None:
        if request.method == 'POST':
            redirect = settings.save_settings(request.form)
            if redirect:
                return redirect
    return settings.show_settings()


@app.route("/iframe/<name>/")
@app.route('/iframe/<name>/<regex("(.*)"):path>')
def iframe(name=None,path='index.html'):
    from thememapper.core.controller.iframe import _IframeController
    editor = _IframeController(settings)
    return editor.show_iframe(name,path)

@app.route("/ajax/<type>/", methods=["POST"])
@app.route("/ajax/<type>/<action>", methods=["POST"])
def ajax(type=None,action=None):
    from thememapper.core.controller.ajax import _AjaxController
    ajax = _AjaxController(settings)
    if type is not None:
        if type == 'rules':
            if request.method == 'POST':
                if action == 'save':
                    return ajax.save_rules(request.form)
                if action is None or action == 'load':
                    return ajax.get_rules(request.form)
    return ajax.abort(204)
