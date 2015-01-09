import pymongo
import motor
import binascii
import os
import functools
from tornado import ioloop, gen
from datetime import timedelta
import pbkdf2

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



class Sessions(dict):
    def __init__(self, *args, **kwargs):
        self.by_username = {}
        super(Sessions, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name == 'by_session_id':
            return self
        super(Sessions, self).__getattr__(name)

    def _common_set(self, session):
        assert isinstance(session, Session)
        username = session.user['username']
        if not username in self.by_username:
            self.by_username[username] = (session,)
        else:
            user_sessions = self.by_username[username]
            for i in range(len(user_sessions)):
                if user_sessions[i].id == session.id:
                    self.by_username[username] = user_sessions[:i] + (session,) + user_sessions[i+1:]
                    break
            else:
                self.by_username[username] += (session,)

    def __setitem__(self, session_id, session):
        self._common_set(session)
        super(Sessions, self).__setitem__(session_id, session)

    def setdefault(self, session_id, default=None):
        session = super(Sessions, self).set_default(session_id, default)
        if not session is default:
            self._common_set(session)
        return session

    def _common_del(self, session):
        assert isinstance(session, Session)
        username = session.user['username']
        user_sessions = self.by_username[username]
        for i in range(len(user_sessions)):
            if user_sessions[i] is session:
                self.by_username[username] = user_sessions[:i] + user_sessions[i+1:]
                break
        else:
            raise AssertionError()
        if not len(self.by_username[username]):
            del self.by_username[username]

    def __delitem__(self, session_id):
        self._common_del(self[session_id])
        super(Sessions, self).__delitem__(session_id)

    def pop(self, session_id, *args, **kwargs):
        session = super(Sessions, self).pop(session_id, *args, **kwargs)
        if not (len(args) and session is args[0]) and not ('default' in kwargs and session is kwargs['default']):
            self._common_del(session)
        return session

    def popitem(self):
        _, session = super(Sessions, self).popitem()
        self._common_del(session)


class Session(object):
    TIMEOUT = 3600
    __slots__ = ['id', 'io_loop', 'timeout', 'user']

    def _expired(self):
        self.unregister()

    def __init__(self, user):
        self.id = None
        self.io_loop = None
        self.timeout = None
        self.user = user

    def register(self, io_loop=None):
        io_loop = io_loop or ioloop.IOLoop.instance()
        for i in range(10):
            id = binascii.hexlify(os.urandom(16))
            if id not in sessions:
                sessions[id] = self
                self.id = id
                break
        if self.id is None:
            raise Exception("failed to register session")
        self.io_loop = io_loop
        self.timeout = self.io_loop.add_timeout(timedelta(seconds=self.TIMEOUT), self._expired)
        print "opened session: " + self.id

    def active(self):
        assert self.id is not None and self.id in sessions
        assert self.io_loop and self.timeout
        self.io_loop.remove_timeout(self.timeout)
        self.timeout = self.io_loop.add_timeout(timedelta(seconds=self.TIMEOUT), self._expired)

    @gen.coroutine
    def update_user(self):
        user = yield db.users.find_one({ 'username': self.user['username'] })
        if not user:
            raise Exception("failed to update user profile")
        self.user = user
# </class Session>

class RPCException(Exception):
    pass
# </class RPCException>

class UserRPC(object):

    @staticmethod
    @gen.coroutine
    def _delete_user(username, current_session=None):
        try:
            user_sessions = sessions.by_username.get(username, ())
            for session in user_sessions:
                if session is not current_session:
                    session.unregister()
            user = yield db.users.find_one({'username': username})
            if not user:
                raise RPCException({'code':100010, 'message': error_codes[100010]})  # no such user
            res = yield db.users.remove({'_id': user['_id']})
            if res['n'] != 1:
                raise RPCException({'code':100001, 'message': error_codes[100001]}) # internal server error
        except pymongo.errors.OperationFailure:
            raise RPCException({'code':100001, 'message': error_codes[100001]}) # internal server error

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
    # </RPCMethod()>

    #################### GUEST ###############################
    @RPCMethod(async=True)
    def register(username, password):
        # IN {"jsonrpc": "2.0", "method": "register", "params": {"username" : "username", "password" : "password"}}
        # OUT {"jsonrpc": "2.0", "method": "register", "params":{"status": "Ok/Error", "message": "success/error code"}}
        if username == "" or password == "":
            raise gen.Return({'status': 'error', 'code': 100014, 'message': error_codes[100014]})  # incorrect input

        user = yield db.users.find_one({'username': username})
        if user:
            raise gen.Return({'status': 'error', 'code': 100007, 'message': error_codes[100007]})  # user already exists

        salt = binascii.hexlify(os.urandom(16))
        pdk = pbkdf2.crypt(password, salt, PBKDF2_ITER)  # 100000 is recommended for SHA256 as of 2013
        user = {'username': username, 'pdk': pdk, 'admin': False, 'active': True}
        yield db.users.save(user)  # this method sets _id in user object
        raise gen.Return({'status': 'ok'})
    # </register()>

    @RPCMethod(async=True)
    def login(username, password):
        # IN {"jsonrpc": "2.0", "method": "login", "params": {"username" : "username", "password" : "password"}}
        # OUT {"jsonrpc": "2.0", "method": "login", "params": {"status" : "Ok/Error", "session_id" : "ssesid", "message" : "success message/error code"}}
        if username == "" or password == "":
            raise gen.Return({'status': 'error', 'code': 100014, 'message': error_codes[100014]})  # incorrect input

        user = yield db.users.find_one({ 'username': username })
        if not user:
            raise gen.Return({'status': 'error', 'code': 100008, 'message': error_codes[100008]})  # invalid username/password

        # get iterations count and salt from stored PDK
        _, _, iterations, salt, _ = user['pdk'].split('$')
        iterations = int(iterations, 16) # convert from hex string

        pdk = pbkdf2.crypt(password, salt, iterations)
        if pdk != user['pdk']:
            raise gen.Return({'status': 'error', 'code': 100008, 'message': error_codes[100008]})  # invalid username/password

        session = Session(user)
        session.register()
        raise gen.Return({'status': 'ok', 'session_id': session.id})
    # </login()>


    @RPCMethod()
    def session_alive(session_id):
        # IN {"jsonrpc": "2.0", "method": "session_alive", "params": {"session_id" : "ssesid"}}
        # OUT {"jsonrpc": "2.0", "method": "session_alive", "params": {"status" : "Ok/Error", "alive": true/false, "message" : "success message/error code"}}
        if session_id in sessions:
            return {'status': 'ok', 'alive': True}
        else:
            return {'status': 'ok', 'alive': False}
    # </session_alive()>


    ################### USER ################################
    @RPCMethod(auth=True)
    def logout(session):
        # IN {"jsonrpc": "2.0", "method": "logout", "params": {"session_id" : "ssesid"}}
        # OUT {"jsonrpc": "2.0", "method": "logout", "params": {"status" : "Ok/Error", "message" : "success message/error code"}}
        session.unregister()
        return {'status': 'ok'}
    # </logout()>

# </class RPCHandlers>


client = motor.MotorClient()
db = client["test"]
sessions = Sessions()




