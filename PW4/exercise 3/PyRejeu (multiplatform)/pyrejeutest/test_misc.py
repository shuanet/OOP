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
import os
import tempfile
from threading import Event
from ivy.std_api import IvyBindMsg, IvyUnBindMsg, IvySendMsg
from pyrejeutest.base import IvyPyRejeuTest


class MiscTest(IvyPyRejeuTest):
    """
    Test case related to misc commands
    """

    def __send_messages(self, messages):
        for m in messages:
            IvySendMsg(m)
            time.sleep(0.1)

    def test_discard_enable(self):
        """Test Discard/Enable commands"""
        f_id = 10002
        evt = Event()
        b_id = IvyBindMsg(lambda *a: evt.set(),
                          "TrackMovedEvent Flight={0} .*".format(f_id))

        IvySendMsg("ClockStart")
        self.assertTrue(evt.wait(3.0), "TrackMovedEvent not received")
        IvySendMsg("ClockStop")

        # disable flight 10002
        self.__send_messages((
            "Discard Flight={0}".format(f_id),
            "SetClock Time=11:24:31",
            "ClockStart"
        ))
        evt.clear()
        time.sleep(2.0)
        self.assertEqual(evt.is_set(), False)
        IvySendMsg("ClockStop")
        # re-enable flight 10002
        self.__send_messages((
            "Enable Flight={0}".format(f_id),
            "SetClock Time=11:25:19",
            "ClockStart"
        ))
        evt.clear()
        self.assertTrue(evt.wait(3.0), "TrackMovedEvent not received")
        IvySendMsg("ClockStop")
        IvyUnBindMsg(b_id)

    def test_discard_all(self):
        """Test DiscardAll command"""
        f_id = 10001
        evt = Event()
        b_id = IvyBindMsg(lambda *a: evt.set(),
                          "TrackMovedEvent Flight={0} .*".format(f_id))

        self.__send_messages((
            "DiscardAll",
            "SetClock Time=12:05:03",
            "ClockStart"
        ))
        evt.clear()
        time.sleep(2.0)
        self.assertEqual(evt.is_set(), False)

        # reset pyrejeu state
        self.__send_messages((
            "ClockStop",
            "Enable Flight=10001",
            "Enable Flight=10002",
        ))
        IvyUnBindMsg(b_id)

    def test_file_write(self):
        """Test FileWrite command after an order which extends the traj"""
        f_id = 10001

        # extend the trajectory
        IvySendMsg("SetClock Time=12:30:00")
        time.sleep(0.1)
        IvySendMsg("AircraftHeading Flight={0} To={1}".format(f_id, 0))
        time.sleep(0.1)

        tmp_dir = tempfile.TemporaryDirectory()
        tmp_dump_file = os.path.join(tmp_dir.name, "dump.txt")
        # save the new dump
        IvySendMsg("FileWrite Type=dump Name={0}".format(tmp_dump_file))
        time.sleep(0.1)
        # test some basic stuff
        data = self.__parse_dump_file(tmp_dump_file)
        self.assertEqual(data["n_beacons"], 1850)
        self.assertEqual(len(data["flights"]), 2)
        self.assertTrue(data["flights"][0].startswith("$ 10001 11:58:00 "
                                                      "12:45:00 40 119 SFA44"))

        tmp_dir.cleanup()
        # cancel the order
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))
        time.sleep(0.1)

    def __parse_dump_file(self, dump_file):
        file_infos = {
            "flights": [],
            "n_beacons": 0
        }
        with open(dump_file) as dump_hd:
            for line in dump_hd:
                if line.startswith("$ "):
                    file_infos["flights"].append(line)
                elif line.startswith("NBeacons"):
                    b_infos = line.split()
                    file_infos["n_beacons"] = int(b_infos[1])
        return file_infos
