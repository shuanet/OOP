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


from pyrejeu.format import RpcError, NOT_WELLFORMED_ERROR, METHOD_NOT_FOUND
from pyrejeu.format import INVALID_METHOD_PARAMS


class BaseBusObject(object):

    def __init__(self):
        self._subscriptions = {}

    def subscribe(self, sub):
        self._subscriptions[sub["name"]] = {
            "callback": sub["callback"],
            "params": sub["params"]
        }

    def connect(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def rpc_answer(self, answer):
        raise NotImplementedError

    def publish_event(self, evt):
        raise NotImplementedError

    #
    # Internal functions
    #
    def get_callback(self, cmd):
        for key in ("method", "params", "id"):
            if key not in cmd:
                err = "%s key is missing" % key
                self.rpc_answer(RpcError(-1, err, code=NOT_WELLFORMED_ERROR))
                return None

        if cmd["method"] not in self._subscriptions:
            err = "%s method does not exist" % cmd["method"]
            self.rpc_answer(RpcError(cmd["id"], err, code=METHOD_NOT_FOUND))
            return None
        return self._subscriptions[cmd["method"]]["callback"]

    def get_params(self, cmd):
        p_list = self._subscriptions[cmd["method"]]["params"]
        params = []

        for idx, p in enumerate(p_list):
            if p["type"] == "choices":
                found = False
                for name in p["name"]:
                    if name in cmd["params"]:
                        found = True
                        params.extend([name, cmd["params"][name]])
                        break
                if not found:
                    err = "parameters %s is missing" % str(p["name"])
                    self.rpc_answer(RpcError(cmd["id"], err,
                                    code=INVALID_METHOD_PARAMS))
                    return None

            elif p["name"] not in cmd["params"] \
                    and ("optional" not in p or not p["optional"]):
                err = "parameters %s is missing" % p["name"]
                self.rpc_answer(RpcError(cmd["id"], err,
                                code=INVALID_METHOD_PARAMS))
                return None

            elif p["name"] in cmd["params"]:
                params.append(cmd["params"][p["name"]])
        return params
