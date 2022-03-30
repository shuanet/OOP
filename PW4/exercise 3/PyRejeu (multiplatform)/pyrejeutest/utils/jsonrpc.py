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

import time
import json


def parse_response(response):
    try:
        return json.loads(response.decode())
    except Exception as ex:
        return {}


def parse_event(evt):
    return evt.decode()


class JSONRPCRequest(object):
    """
    Build JSON-RPC Request
    """
    def __init__(self, method_name, params, notification=False, id=None):
        self.method = method_name
        self.params = params
        # use timestamp as id if no id has been given
        self.id = None
        if not notification:
            self.id = id or int(time.time())

    def _build_obj(self):
        return {"method": self.method, "params": self.params, "id": self.id}

    def get_id(self):
        return self.id

    def dump(self):
        return json.dumps(self._build_obj()).encode()
