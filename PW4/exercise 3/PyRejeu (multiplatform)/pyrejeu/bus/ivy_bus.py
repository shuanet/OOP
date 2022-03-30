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
from ivy.std_api import IvyApplicationDisconnected, IvyInit, IvyStart, IvyStop
from ivy.std_api import IvySendMsg, IvyBindMsg


class IvyBus(object):
    NAME = "ivy"
    REGEXP_SYNTAX = {
        "int": "\d+",
        "float": "\S+",
        "string": "\S+",
        "string_list": ".*",
        "bool": "[01]"
    }

    def __init__(self, bus_id, app_name, logging_level):
        self.bus_id = bus_id
        self.app_name = app_name
        # set ivy logger to the right level
        ivy_logger = logging.getLogger('Ivy')
        ivy_logger.setLevel(logging_level)

    def __on_cx_proc(self, agent, connected):
        if connected == IvyApplicationDisconnected:
            logging.info('Ivy application %r was disconnected', agent)
        else:
            logging.info('Ivy application %r was connected', agent)

    def __on_die_proc(self, agent, _id):
        logging.info('received the order to die from %r with id = %d',
                     agent, _id)

    def connect(self):
        IvyInit(self.app_name, "%s READY" % self.app_name, 0,
                self.__on_cx_proc, self.__on_die_proc)
        IvyStart(self.bus_id)

    def close(self):
        IvyStop()

    def rpc_answer(self, answer):
        ivy_fmt_ans = answer.to_ivy_fmt()
        if isinstance(ivy_fmt_ans, str):
            IvySendMsg(ivy_fmt_ans)
        elif isinstance(ivy_fmt_ans, list):
            for msg in ivy_fmt_ans:
                IvySendMsg(msg)

    def publish_event(self, evt):
        IvySendMsg(evt.to_ivy_fmt())

    def __build_regexp(self, p):
        if p["type"] != "choices":
            return "{0}=({1})".format(p["name"], self.REGEXP_SYNTAX[p["type"]])
        return "({0})=(\S+)".format("|".join(p["name"]))

    def subscribe(self, sub):
        msg_id_type = "none"
        if "ivyMsgId" in sub:
            msg_id_type = sub["ivyMsgId"]
            if sub["ivyMsgId"] == "MsgName":
                sub["params"] = [
                    {"name": "MsgName", "type": "string"}
                ] + sub["params"]

        reg_exp = r'^%s' % sub["name"]
        attrs = [self.__build_regexp(p) for p in sub["params"]
                 if "optional" not in p or not p["optional"]]
        if len(attrs) > 0:
            reg_exp += " %s" % " ".join(attrs)
        regexp_list = [reg_exp]

        # handle optional params with new regexp
        o_attrs = [self.__build_regexp(p) for p in sub["params"]
                   if "optional" in p and p["optional"]]
        for idx, o_attr in enumerate(o_attrs):
            r = "{0} {1}".format(reg_exp, " ".join(o_attrs[:idx+1]))
            regexp_list.append(r)

        def callback(*l):
            msg_id = None
            l_idx = 1
            if msg_id_type == "agent":
                msg_id = l[0]
            elif msg_id_type == "MsgName":
                l_idx = 2
                msg_id = l[1]
            sub["callback"](msg_id, *l[l_idx:])
        for r in regexp_list:
            IvyBindMsg(callback, r)
