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


from threading import Thread, Event
import logging
import pika
from pyrejeu.bus.base import BaseBusObject
from pyrejeu.format import parse_request


class AmqpBus(BaseBusObject):
    NAME = "amqp"
    RPC_QUEUE_NAME = "pyrejeu_rpc_queue"
    EVENT_EX_NAME = "pyrejeu_event_exchange"

    def __init__(self, amqp_url):
        super(AmqpBus, self).__init__()
        self._response = None

        # amq params
        self._connection = None
        self._channel = None
        self._evt_lock = Event()
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url

    def connect(self):
        logging.info('AMQP -- Connecting to %s', self._url)
        self._connection = pika.SelectConnection(pika.URLParameters(self._url),
                                                 self.on_connection_open,
                                                 stop_ioloop_on_close=True)
        self._connection.add_on_close_callback(self.on_connection_closed)
        Thread(target=self._connection.ioloop.start).start()

    def on_connection_open(self, unused_connection):
        logging.debug('AMQP -- Connection opened')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        self._evt_ch = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logging.warning("Connection closed, reopening in 5 seconds: "
                            "(%s) %s", reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_channel_open(self, channel):
        logging.debug('AMQP -- Channel opened')
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.queue_declare(self.on_queue_declareok, self.RPC_QUEUE_NAME)

        # create new exchange/queue for event
        self._channel.exchange_declare(lambda *a: self._evt_lock.set(),
                                       self.EVENT_EX_NAME,
                                       'topic')

    def on_channel_closed(self, channel, reply_code, reply_text):
        logging.warning('Channel %i was closed: (%s) %s',
                        channel, reply_code, reply_text)
        self._connection.close()

    def on_queue_declareok(self, method_frame):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_request,
                                                         self.RPC_QUEUE_NAME)

    def on_consumer_cancelled(self, method_frame):
        logging.info('Consumer was cancelled remotely, shutting down: %r',
                     method_frame)
        if self._channel:
            self._channel.close()

    def on_request(self, unused_channel, basic_deliver, props, body):
        cmd = parse_request(body)
        cb_func = self.get_callback(cmd)
        if cb_func is not None:
            params = self.get_params(cmd)
            if params is not None:
                cb_func(cmd["id"], *params)
        properties = pika.BasicProperties(correlation_id=props.correlation_id)
        self._channel.basic_ack(basic_deliver.delivery_tag)
        self._channel.basic_publish(exchange='',
                                    routing_key=props.reply_to,
                                    properties=properties,
                                    body=self._response.dump())

    def close(self):
        self._closing = True
        if self._channel:
            self._channel.basic_cancel(lambda *a: self._channel.close(),
                                       self._consumer_tag)

    def rpc_answer(self, answer):
        self._response = answer

    def publish_event(self, evt):
        self._evt_lock.wait(timeout=3.0)
        topic = "evt.%s" % evt.evt_name
        self._channel.basic_publish(exchange=self.EVENT_EX_NAME,
                                    routing_key=topic,
                                    body=evt.dump())
