import pymongo
import motor
import binascii
import signal
import os
import sys
import errno
import functools
from tornado import ioloop, web, gen, escape
from datetime import timedelta
import pbkdf2
import getopt
import ConfigParser
from plugins.users import userrpc

PBKDF2_ITER = 10000

is_closing = False
config = {}  # TODO create class
error_codes = {
    100000: "not implemented",
    100001: "internal server error",
    100002: "incorrect RPC call",
    100003: "unknown method",
    100004: "authentication required",
    100005: "permission denied",
    100006: "invalid approval code",
    100007: "username already exists",
    100008: "invalid username/password",
    100009: "old password is invalid",
    100010: "no such user",
    100011: "Fetching of sessions data failed",
    100012: "incorrect ajax call",
    100013: "new and old passwords are the same",
    100014: "incorrect input"
}

templates = {'errors': {}}


def sigHandler(signum, frame):
    global is_closing
    print '\nexiting...'
    is_closing = True
## signal_handler
#############################################################################


def try_exit():
    """
    try_exit should close all unfinished ...
    """
    global is_closing
    if is_closing:
        ioloop.IOLoop.instance().stop()
        print 'exit success'
## try_exit
#############################################################################


def load_config(config_file):
    """
    Tries to open configuration file and load
    parameters from it
    """
    config_file = os.path.realpath(config_file)
    if not os.path.exists(config_file):
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), config_file)

    cfg = ConfigParser.ConfigParser()

    cfg.read(config_file)

    par = {}
    par.update(cfg.items('main_section'))
    par.update(cfg.items('server_section'))

    return par
## load_config
#############################################################################


class ErrorHandler(web.ErrorHandler):
    """Generates an error response with status_code for all requests."""
    def write_error(self, status_code, **kwargs):
        try:
            self.finish(templates['errors'][status_code])
        except KeyError:
            super(ErrorHandler, self).write_error(status_code, **kwargs)

# override the tornado.web.ErrorHandler with our default ErrorHandler
web.ErrorHandler = ErrorHandler


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        session_id = self.get_secure_cookie('session_id')
        if session_id is None or not session_id in sessions:
            self.clear_cookie('session_id')
            return None
        return session_id

    @gen.coroutine
    def get_current_user_object(self):
        try:
            session = sessions[self.current_user]
            user = session.user
            raise gen.Return(user)
        except KeyError:
            raise gen.Return(None)


class AjaxHandler(BaseHandler):

    @web.asynchronous
    @gen.coroutine
    def post(self):
        data = escape.json_decode(self.request.body)

        try:
            method = getattr(userrpc.UserRPC, data['method'])
        except KeyError:
            res = {'status': 'error', 'code': 100012, 'message': error_codes[100012]}  # incorrect ajax call
        except AttributeError:
            res = {'status': 'error', 'code': 100003, 'message': error_codes[100003]}  # unknown method
        else:
            if not 'params' in data:
                data['params'] = {}
            if method.auth:
                data['params']['session_id'] = self.current_user
            try:
                res = yield method(**data['params'])
            except Exception:
                res = {'status': 'error', 'code': 100001, 'message': error_codes[100001]}   # internal server error
                self.finish(res)
                raise

            if method == userrpc.UserRPC.login and res['status'] == 'ok':
                self.set_secure_cookie('session_id', res['session_id'])

        self.write(res)
        self.add_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json')

    def options(self, *args, **kwargs):
        self.add_header('Access-Control-Allow-Origin', '*')
        self.add_header('Access-Control-Allow-Methods', 'POST')
        self.add_header('Access-Control-Allow-Headers', 'accept, content-type')

class RPCHandler(BaseHandler):

    @web.asynchronous
    @gen.coroutine
    def post(self):
        rpcresult = {}
        data = escape.json_decode(self.request.body)

        try:
            method = getattr(userrpc.UserRPC, data['method'])
        except KeyError:
            res = {'status': 'error', 'code': 100002, 'message': error_codes[100002]}  # incorrect RPC call
        except AttributeError:
            res = {'status': 'error', 'code': 100003, 'message': error_codes[100003]}  # unknown method
        else:
            try:
                if type(data['params']) == list:
                    data['params'] = data['params'][0]
                res = yield method(**data['params'])
            except Exception:
                res = {'status': 'error', 'code': 100001, 'message': error_codes[100001]}  # internal server error
                rpcresult["error"] = res
                self.finish(rpcresult)
                raise
        if res["status"] == 'error':
            rpcresult["error"] = res
        else:
            rpcresult["result"] = res
        self.write(rpcresult)
        self.add_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json')

    def options(self, *args, **kwargs):
        self.add_header('Access-Control-Allow-Origin', '*')
        self.add_header('Access-Control-Allow-Methods', 'POST')
        self.add_header('Access-Control-Allow-Headers', 'accept, content-type')


class ConfigFileHandler(web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(ConfigFileHandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        # Ignore 'path'.
        super(ConfigFileHandler, self).get(self.filename, include_body)

    def get_content_type(self):
        mime_type = super(ConfigFileHandler, self).get_content_type()
        if mime_type is None:
            mime_type = "application/octet-stream"
        return mime_type


class MainHandler(BaseHandler):
    @web.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        user = yield self.get_current_user_object()
        self.render("webapp/index.html", user=user["username"])

settings = {
    "cookie_secret": "61oETzKXQOGaYdkL5gEmGeJJFuYh7EQnp2CdTP1o/Vo=",
    "login_url": "/index.html",
    "debug": True,
}

client = motor.MotorClient()
db = 'localhost:27017'
sessions = userrpc.Sessions()

application = web.Application([
    (r"/ajax", AjaxHandler),
    (r"/rpc", RPCHandler),
    (r"/", MainHandler),
    (r"/(.*)", web.StaticFileHandler, {"path": "./webapp/"}),
    (r"/(favicon.ico)",  web.StaticFileHandler, {"path": "./webapp/"})
], **settings)

signal.signal(signal.SIGINT, sigHandler)


def RunApp(arguments=""):
    global config
    global db
    if "config" in arguments.keys() != False:
        config_file = arguments["config"]
    else:
        config_file = 'config.cfg'

    try:
        config = load_config(config_file)
    except OSError, e:
        print "Failed to load parameters from %s" % config_file
        sys.exit(1)
    db = client[config["db_name"]]
    port = config["webapp_port"]
    address = config["webapp_address"]
    application.listen(port, address)


    ioloop.PeriodicCallback(try_exit, 100).start()
    ioloop.IOLoop.instance().start()
## RunApp
#############################################################################

if __name__ == "__main__":
    #Parse Args
    arguments = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError as e:
        print "Got error while parsing args: %s " % e
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            arguments["config"] = arg

    # load templates
    with open('./webapp/404.html', 'rb') as _f:
        templates['errors'][404] = _f.read()

    RunApp(arguments)