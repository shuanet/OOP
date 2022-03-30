#!/usr/bin/env python3
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
import sys
import re
from optparse import OptionParser
import cmd
import pprint
import uuid
from queue import Queue
from threading import Thread

# zmq support
try:
    import zmq
except ImportError:
    zmq = None
# amqp support
try:
    import pika
except ImportError:
    pika = None


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


class BaseClientShell(cmd.Cmd):
    intro = 'Welcome to zmq client for PyRejeu'
    prompt = '[pyrejeu-client] '

    def __init__(self):
        super(BaseClientShell, self).__init__()
        self.events = Queue(maxsize=1000)

    def display_response(self, rsp, answer_type):
        answer = json.loads(rsp.decode())
        if "error" in answer:
            err = answer["error"]
            print("ERROR : %s -- %s" % (err["code"], err["message"]))
            return

        if answer_type == "ack":
            print("OK")
        else:
            pprint.pprint(answer["result"])

    def record_event(self, evt):
        if self.events.qsize() >= 900:
            self.events.get()
        self.events.put(evt.decode())

    def send_command(self, cmd_name, args={}, answer_type="ack"):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def parse_args(self, arg, a_list):
        r_args = {}

        args = arg.split()
        if len(args) != len(a_list):
            return self.error("Wrong number of params")

        for idx, (a_name, a_type) in enumerate(a_list):
            a_value = args[idx]
            if a_type == "int":
                try:
                    a_value = int(a_value)
                except ValueError:
                    return self.error("Arg %s is not an integer", a_value)
            elif a_type == "float":
                try:
                    a_value = float(a_value)
                except ValueError:
                    return self.error("Arg %s is not a float", a_value)
            elif a_type == "time":
                if not re.match("^\d{2}:\d{2}:\d{2}$", a_value):
                    return self.error("%s is not a time following "
                                      "format HH:MM:SS", a_value)
            r_args[a_name] = a_value
        return r_args

    def do_FileWrite(self, arg):
        args = self.parse_args(arg, [("Name", "string")])
        args["Type"] = "dump"
        self.send_command("FileWrite", args=args)

    def do_ClockStart(self, arg):
        'Send ClockStart command to PyRejeu'
        self.send_command("ClockStart")

    def do_ClockStop(self, arg):
        'Send ClockStop command to PyRejeu'
        self.send_command("ClockStop")

    def do_ClockDatas(self, arg):
        'Send GetClockDatas command to PyRejeu'
        self.send_command("GetClockDatas", answer_type="dict")

    def do_SetClock(self, arg):
        'Send SetClock Time= command to PyRejeu: Ex: SetClock 12:00:00'
        args = self.parse_args(arg, [("Time", "time")])
        self.send_command("SetClock", args=args)

    def do_DataBaseInfos(self, arg):
        """Send GetDataBaseInfos command to PyRejeu:
        ex: DataBaseInfos AircraftType=A320"""
        self.send_command("GetDataBaseInfos", args={"Cond": arg},
                          answer_type="dict")

    def do_Position(self, arg):
        'Send GetPosition command to PyRejeu. Ex: GetPosition 101 12:00:00'
        args = self.parse_args(arg, [("Flight", "int"), ("Time", "time")])
        self.send_command("GetPosition", args=args, answer_type="dict")

    def do_LastEvents(self, arg):
        "Show the last 10 received events"
        i = 0
        while not self.events.empty() and i < 10:
            print(self.events.get())
            i += 1

    def do_bye(self, arg):
        'exit:  BYE'
        print('Leaving pyrejeu client')
        self.close()
        return True

    def error(self, msg, *args):
        msg = msg % args
        print("ERROR: %s" % msg)
        return None


class ZmqShell(BaseClientShell):

    def __init__(self, host, port, evt_port):
        super(ZmqShell, self).__init__()
        self.rpc_socket = zmq.Context().socket(zmq.REQ)
        self.rpc_socket.connect("tcp://{0}:{1}".format(host, port))

        self.running = True
        self.evt_thread = Thread(target=self.recv_events,
                                 args=(host, evt_port,))
        self.evt_thread.start()

    def recv_events(self, host, evt_port):
        evt_socket = zmq.Context().socket(zmq.SUB)
        evt_socket.connect("tcp://%s:%s" % (host, evt_port))
        # subscribe to all events
        evt_socket.setsockopt(zmq.SUBSCRIBE, b'')

        poller = zmq.Poller()
        poller.register(evt_socket, zmq.POLLIN)
        while self.running:
            evts = dict(poller.poll(timeout=0.1))
            if evt_socket in evts:
                self.record_event(evt_socket.recv())
        evt_socket.close()

    def send_command(self, cmd_name, args={}, answer_type="ack"):
        request = JSONRPCRequest(cmd_name, args)
        self.rpc_socket.send(request.dump())
        self.display_response(self.rpc_socket.recv(), answer_type)

    def close(self):
        self.running = False
        self.evt_thread.join()
        self.rpc_socket.close()


class AmqpShell(BaseClientShell):
    rpc_queue_name = "pyrejeu_rpc_queue"
    evt_exchange = "pyrejeu_event_exchange"

    def __init__(self, url):
        super(AmqpShell, self).__init__()

        self.connection = pika.BlockingConnection(pika.URLParameters(url))
        self.channel = self.connection.channel()
        # rpc commands
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

        # receive events
        self.events = Queue(maxsize=1000)
        self.channel.exchange_declare(exchange=self.evt_exchange, type='topic')
        result = self.channel.queue_declare(exclusive=True)
        self.evt_queue = result.method.queue
        self.channel.queue_bind(exchange=self.evt_exchange,
                                queue=self.evt_queue,
                                routing_key="evt.*")
        self.channel.basic_consume(self.on_event, no_ack=True,
                                   queue=self.evt_queue)

        # launch loop to handle received messages
        self.running = True
        self.thread = Thread(target=self.start_consuming)
        self.thread.start()

    def start_consuming(self):
        while self.running:
            self.connection.process_data_events(time_limit=0.1)

    def on_event(self, ch, method, props, body):
        self.record_event(body)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def send_command(self, cmd_name, args={}, answer_type="ack"):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        request = JSONRPCRequest(cmd_name, args)
        self.channel.basic_publish(exchange='',
                                   routing_key='pyrejeu_rpc_queue',
                                   properties=pika.BasicProperties(
                                        reply_to=self.callback_queue,
                                        correlation_id=self.corr_id,
                                   ),
                                   body=request.dump())
        while self.response is None:
            time.sleep(0.1)

        self.display_response(self.response, answer_type)

    def close(self):
        self.running = False
        self.thread.join()
        self.connection.close()


if __name__ == "__main__":
    usage = "usage: %prog <bus_id>"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        sys.exit("Error: bus id is missing")

    m = re.match(r"^zmq://(?P<host>[A-Za-z\d\.]+):"
                 "(?P<r_p>[0-9]+):(?P<e_p>[0-9]+)$", args[0])
    if m is not None:
        if zmq is not None:
            ZmqShell(*m.group("host", "r_p", "e_p")).cmdloop()
        else:
            sys.exit("You must install pyzmq to use ZMQ framawork")
    elif args[0].startswith("amqp://"):
        if pika is not None:
            AmqpShell(args[0]).cmdloop()
        else:
            sys.exit("You must install pika to use AMQP protocol")
    else:
        sys.exit("Error: wrong bus id")