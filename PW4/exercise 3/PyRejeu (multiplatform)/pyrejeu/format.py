# -*- coding: utf-8 -*-
# PyRejeu, an air traffic replay tool
# Copyright (C) 2017 Mickael Royer <mickael.royer@enac.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import logging
import json

NOT_WELLFORMED_ERROR = -32700
INVALID_JSONRPC = -32600
METHOD_NOT_FOUND = -32601
INVALID_METHOD_PARAMS = -32602
INTERNAL_ERROR = -32603
METHOD_NOT_CALLABLE = -32604


def parse_request(request):
    try:
        return json.loads(request.decode())
    except Exception as ex:
        logging.error("Unable to parse request %s", request)
        return {}


class RpcAnswer(object):

    def to_json(self):
        raise NotImplementedError

    def dump(self):
        return json.dumps(self.to_json()).encode()


class RpcError(RpcAnswer):

    def __init__(self, c_id, message, code=INTERNAL_ERROR):
        self.c_id = c_id
        self.code = code
        self.message = message

    def to_ivy_fmt(self):
        # legacy rejeu does not send error message
        return None

    def to_json(self):
        return {
            "id": int(self.c_id),
            "error": {
                "code": self.code,
                "message": self.message
            }
        }


class RpcAck(RpcAnswer):

    def __init__(self, c_id):
        self.c_id = c_id

    def to_ivy_fmt(self):
        # legacy rejeu does not ack for simple command (like ClockStart)
        return None

    def to_json(self):
        return {
            "id": int(self.c_id),
            "result": True
        }


class RpcResult(RpcAnswer):

    def __init__(self, c_id, msg_id, attrs):
        self.c_id = c_id
        self.msg_id = msg_id
        self.attrs = attrs

    def to_ivy_fmt(self):
        attrs = ["{0}={1}".format(k, v) for k, v in self.attrs]
        if self.c_id is not None:
            return "{0} {1} {2}".format(self.msg_id, self.c_id,
                                        " ".join(attrs))
        else:
            return "{0} {1}".format(self.msg_id, " ".join(attrs))

    def to_json(self):
        return {
            "id": int(self.c_id),
            "result": dict(self.attrs)
        }


class RpcListResult(RpcAnswer):

    def __init__(self, c_id, msg_id, lst, slice_size=50):
        self.c_id = c_id
        self.msg_id = msg_id
        self.lst = lst
        self.slice_size = slice_size

    def to_ivy_fmt(self):
        ans_lst = []

        s = int(self.slice_size)
        nb_msg = (len(self.lst)//s) + 1
        for i in range(0, nb_msg):
            first, last = s*i, min(s*(i+1), len(self.lst))
            data = " ".join(self.lst[first:last])
            if data != "":
                ans_lst.append("{0} {1} Slice={2}".format(self.msg_id,
                                                          self.c_id, data))
        ans_lst.append("{0} {1} EndSlice".format(self.msg_id, self.c_id))
        return ans_lst

    def to_json(self):
        return {
            "id": int(self.c_id),
            "result": self.lst
        }


class Event(object):

    def __init__(self, evt_name, attrs):
        self.evt_name = evt_name
        self.attrs = attrs

    def to_ivy_fmt(self):
        attrs = ["{0}={1}".format(k, v) for k, v in self.attrs]
        return "{0} {1}".format(self.evt_name, " ".join(attrs))

    def dump(self):
        attrs = ["{0}={1}".format(k, v) for k, v in self.attrs]
        return "{0} {1}".format(self.evt_name, " ".join(attrs)).encode()
