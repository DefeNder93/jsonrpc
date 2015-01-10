import pymongo
import motor
import functools
from tornado import gen
from plugins.users.userrpc import Sessions

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


class FeedRPC(object):

    # Decorator for RPC methods
    def RPCMethod(async=False, auth=False, admin=False):
        def decor(f):
            assert (admin and auth) or not admin
            f.RPC = True
            f.async = async
            f.auth = auth
            f.admin = admin
            if async:
                f = gen.coroutine(f)

            @gen.coroutine
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                if auth:
                    if 'session_id' in kwargs:
                        session_id = kwargs.pop('session_id')
                        kw = True
                    elif len(args) >= 1:
                        session_id = args[0]
                        kw = False
                    else:
                        raise TypeError("invalid parameters for RPC call")
                    if session_id not in sessions:
                        raise gen.Return({'status': 'error', 'code': 100004, 'message': error_codes[100004]})  # authentication required
                    session = sessions[session_id]
                    session.active()
                    if kw:
                        kwargs['session'] = session
                    else:
                        args[0] = session
                    if admin:
                        if not session.user['admin']:
                            raise gen.Return({'status': 'error', 'code': 100005, 'message': error_codes[100005]})  # permission denied
                if async:
                    res = yield f(*args, **kwargs)
                else:
                    res = f(*args, **kwargs)
                raise gen.Return(res)
            # </wrapper()>
            return staticmethod(wrapper)
        # </decor()>
        return decor
    # </RPCMethod()

    ################### NEWS ##################################
    @RPCMethod(async=True)
    def post_news(session, username, time, theme, news):
        # IN {"jsonrpc": "2.0", "method": "post_news", "params": {"session" : "ssesid", "username": "username", "time": "time", "theme": "theme", "news": "text"}}
        # OUT {"jsonrpc": "2.0", "method": "post_news", "params": {"status" : "Ok/Error", "message" : "success message/error code"}}
        news_query = {"username": username, "time": time, "theme": theme,  "news": news}
        yield db.news.save(news_query)  # this method sets _id in user object
        raise gen.Return({'status': 'ok'})
    # </post_news()>

    ##############################################################
    @RPCMethod(async=True)
    def load_news(news):
        # IN {"jsonrpc": "2.0", "method": "load_news", "params": {"news": "true"}}
        # OUT {"jsonrpc": "2.0", "method": "load_news", "params": {"status" : "Ok/Error", "message" : "success message/error code", "news_list": "news_list"}}
        news_list = []
        cursor = db.news.find({}, {'_id': False})
        for news in (yield cursor.to_list(length=200)):
            news_list.append(news)
        raise gen.Return({'status': 'ok', 'news': news_list})
    # </load_news()>

# </class RPCHandlers>


client = motor.MotorClient()
db = client["test"]
sessions = Sessions()

