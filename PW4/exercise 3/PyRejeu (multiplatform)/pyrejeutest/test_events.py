
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

from threading import Event
from ivy.std_api import IvyUnBindMsg, IvyBindMsg, IvySendMsg
from pyrejeutest.base import IvyPyRejeuTest


class EventsTest(IvyPyRejeuTest):
    """
    Test case used to validate the syntax of events
    generated by PyRejeu
    """

    def test_track_event(self):
        """Test TrackMovedEvent syntax"""
        self.evt = Event()
        self.event_data = ""

        def on_evt(*l):
            self.event_data += l[1]
            self.evt.set()
        b_id = IvyBindMsg(on_evt, "TrackMovedEvent (.*)")
        IvySendMsg("ClockStart")
        self.assertTrue(self.evt.wait(timeout=3.0))
        self.assertEqual(self.event_data, "Flight=10002 CallSign=SFA438 "
                                          "Ssr=1000 Sector=-- Layers=F "
                                          "X=106.00 Y=-154.00 Vx=-53.00 "
                                          "Vy=-55.00 Afl=20 Rate=1311 "
                                          "Heading=223 GroundSpeed=76 "
                                          "Tendency=1 Time=11:24:00")
        IvySendMsg("ClockStop")
        IvyUnBindMsg(b_id)