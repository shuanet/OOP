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


from threading import Thread
import zmq
from pyrejeu.bus.base import BaseBusObject
from pyrejeu.format import parse_request


class ZmqBus(BaseBusObject):
    NAME = "zmq"

    def __init__(self, host, rpc_port, event_port):
        super(ZmqBus, self).__init__()
        self.host = host
        self.rpc_port = rpc_port
        self.event_port = event_port
        self.__thread = None
        self.__running = True

        # create sockets
        self.context = zmq.Context()
        self.rpc_socket = self.context.socket(zmq.REP)
        self.evt_socket = self.context.socket(zmq.PUB)

    def connect(self):
        # launch thread to receive commands
        self.__thread = Thread(target=self.__connect)
        self.__thread.start()

    def __connect(self):
        self.rpc_socket.bind("tcp://{0}:{1}".format(self.host, self.rpc_port))
        self.evt_socket.bind("tcp://{0}:{1}".format(self.host, self.event_port))

        poller = zmq.Poller()
        poller.register(self.rpc_socket, zmq.POLLIN)
        while self.__running:
            evts = dict(poller.poll(100))
            if self.rpc_socket in evts and evts[self.rpc_socket] == zmq.POLLIN:
                cmd = parse_request(self.rpc_socket.recv())
                cb_func = self.get_callback(cmd)
                if cb_func is not None:
                    params = self.get_params(cmd)
                    if params is not None:
                        cb_func(cmd["id"], *params)

        for s in self.evt_socket, self.rpc_socket:
            s.close()

    def close(self):
        self.__running = False
        if self.__thread is not None:
            self.__thread.join()

    def rpc_answer(self, answer):
        self.rpc_socket.send(answer.dump())

    def publish_event(self, evt):
        self.evt_socket.send(evt.dump())
