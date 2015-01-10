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
    100014: "incorrect input",
    100015: "contact list is empty",
    100016: "user already exists in your contact list",
    100017: "user not exists"
}

templates = {'errors': {}}


class ChatRPC(object):

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

    ################### CHAT ##################################
    @RPCMethod(async=True)
    def send_msg(session_id, sender, recipient_list, submit_time, msg_type, group, msg):
        # IN {"jsonrpc": "2.0", "method": "send_msg", "params": {"session_id" : "ssesid", "sender": "sender_id", "recipient_list":
        #    {"recipient_id": "recipient_id", "delivered":0}, "submit_time": "time", "type": "msg/add", "group": "__user__/group name", "msg": "text"}}
        # OUT {"jsonrpc": "2.0", "method": "send_msg", "params": {"status" : "Ok/Error", "message" : "success message/error code"}}

        _user_arr  = []
        # get recipient from db
        for rec in recipient_list:
            user = yield db.users.find_one({ 'username': rec["recipient_id"] })
            if not user:
                raise gen.Return({'status': 'error', 'code': 100008, 'message': error_codes[100008]})  # invalid username
            _user_arr.append({"rec": user["username"], "delivered": 0})

        msg_query = {"sender": sender,"recipient_list": _user_arr, "submit_time": submit_time, "type": msg_type, "group": group, "msg": msg}
        yield db.messages.save(msg_query)  # this method sets _id in user object
        raise gen.Return({'status': 'ok'})
    # </send_msg()>

    ##############################################################
    @RPCMethod(auth=True)
    def get_msg(session_id, username):
        # IN {"jsonrpc": "2.0", "method": "get_msg", "params": {"session_id" : "ssesid"}}
        # OUT {"jsonrpc": "2.0", "method": "get_msg", "params": {"status" : "Ok/Error", "alive": true/false, "message" : "success message/error code"}}

        ret_list = []
        msg_list = yield db.messages.find({"recipient_list": {'$elemMatch':
                                                          {
                                                            "rec": "user1",
                                                            "delivered": 0
                                                          }}}, {'_id': False})
        if msg_list == []:
            raise gen.Return({'status': 'ok', 'message': "no messages"})  # user already exists

        for msg in msg_list:
            msg_id = msg["_id"]
            if msg["msg_type"] == "msg":
                pass
            if msg["msg_type"] == "add":
                pass
            if msg["msg_type"] == "del":
                pass

    ##############################################################
    def get_userlist(session_id, username):
        # IN {"jsonrpc": "2.0", "method": "get_userlist", "params": {"session_id" : "ssesid"}}
        # OUT {"jsonrpc": "2.0", "method": "get_userlist", "params": {"status" : "Ok/Error", "alive": true/false, "message" : "success message/error code"}}

        #get user list from db
        userlist = yield db.userlist.find_one({'username': username})
        if not userlist:
            raise gen.Return({'status': 'error', 'code': 100015, 'message': error_codes[100015]})  # contact list is empty
        raise gen.Return({'status': 'ok', 'userlist': userlist})

    # </get_userlist()>

    ##############################################################
    def add_to_userlist(session_id, username, add_username):
        # IN {"jsonrpc": "2.0", "method": "add_to_userlist", "params": {"session_id" : "ssesid"}}
        # OUT {"jsonrpc": "2.0", "method": "add_to_userlist", "params": {"status" : "Ok/Error", "alive": true/false, "message" : "success message/error code"}}

        # check if user exists
        user = yield db.users.find_one({ 'username': add_username })
        if not user:
            raise gen.Return({'status': 'error', 'code': 100017, 'message': error_codes[100017]})  # username not exists

        userlist = yield db.userlist.find_one({'username': username})
        if not userlist:
            db.userlist.save({"owner": username, "userlist":[]})
        if userlist:
            raise gen.Return({'status': 'error', 'code': 100016, 'message': error_codes[100016]})  # user already exists in your contact list


        raise gen.Return({'status': 'ok'})
    # </add_to_userlist()>

    ##############################################################
    def del_from_userlist(session_id, username, del_username):
        # IN {"jsonrpc": "2.0", "method": "del_from_userlist", "params": {"session_id" : "ssesid"}}
        # OUT {"jsonrpc": "2.0", "method": "del_from_userlist", "params": {"status" : "Ok/Error", "alive": true/false, "message" : "success message/error code"}}
        raise gen.Return({'status': 'ok'})
    # </del_from_userlist()>

    ##############################################################

# </class RPCHandlers>


client = motor.MotorClient()
db = client["test"]
sessions = Sessions()

