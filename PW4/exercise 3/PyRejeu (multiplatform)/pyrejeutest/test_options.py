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

import unittest
from threading import Event
from queue import LifoQueue
from ivy.std_api import IvyBindMsg, IvyUnBindMsg
from pyrejeutest.base import IVY_BUS_ID
from pyrejeutest.utils.server import TestServer


class PyRejeuOptionsTest(unittest.TestCase):

    def setUp(self):
        self.test_server = TestServer()

    def tearDown(self):
        self.test_server.stop()

    def test_start_option(self):
        event = Event()
        evt_queue = LifoQueue(maxsize=1000)

        def on_clock_event(*larg):
            event.set()
            evt_queue.put({
                "Time": larg[1]
            })
        b_id = IvyBindMsg(on_clock_event, "^ClockEvent Time=(\S+) Rate=(\S+)")

        # test -s auto option
        self.test_server.start("-b ivy://%s -s auto" % IVY_BUS_ID)

        self.assertTrue(event.wait(timeout=3.0), "ClockEvent msg not received")
        last_msg = evt_queue.get()
        self.assertEqual(last_msg, {
            "Time": '11:24:01'
        })
        self.test_server.stop()

        # test -s auto option
        event.clear()
        self.test_server.start("-b ivy://%s -s 11:55:05" % IVY_BUS_ID)

        self.assertTrue(event.wait(timeout=3.0), "ClockEvent msg not received")
        last_msg = evt_queue.get()
        self.assertEqual(last_msg, {
            "Time": '11:55:06'
        })

        self.test_server.stop()
        IvyUnBindMsg(b_id)
