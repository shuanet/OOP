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


class FlightReadingTest(IvyPyRejeuTest):
    """
    Test case used to validate that pyrejeu answer
    correcly to flight solicitation
    """

    def test_trajectory(self):
        """Test the GetTrajectory command"""
        trajectory = self.get_trajectory(10002)
        trajectory = trajectory.strip()
        self.assertTrue(trajectory.startswith("106.00 -154.00 11:24:00"))

    def test_track(self):
        """Test the GetTrack command"""
        track = self.get_track(10002)
        self.assertEqual(len(track), 355)
        self.assertEqual(track[0], {
            'pos_x': 106.0,
            'pos_y': -154.0,
            'hour': '11:24:00',
            'rate': 1311.0,
            'fl': 20,
            'vit_y': -55.0,
            'vit_x': -53.0,
            'tendency': 1
        })

    def test_pln(self):
        """Test the GetPln command"""
        pln = self.get_pln(10002)
        self.assertEqual(pln["CallSign"], "SFA438")
        self.assertEqual(pln["Rfl"], "80")
        self.assertTrue(pln["List"].startswith("LFCR V 11:24 20"))

        # test From option
        pln = self.get_pln(10002, from_type="11:30:00")
        self.assertTrue(pln["List"].startswith("GAI V 11:44 80"))

        pln = self.get_pln(10002, from_type="LASBO")
        self.assertTrue(pln["List"].startswith("LASBO V 11:55 80"))

    def __get_range(self, flight_id):
        msg_id = self.test_data.get_random_string()
        evt = Event()
        range_infos = {}

        def on_range_msg(agent, f_time, l_time, visible):
            evt.set()
            range_infos.update({
                "l_time": l_time,
                "f_time": f_time,
                "visible": visible,
            })

        b_id = IvyBindMsg(on_range_msg,
                          "Range {0} FirstTime=(\S+) "
                          "LastTime=(\S+) Visible=(\S+)".format(msg_id))
        # test for all flight
        IvySendMsg("GetRange MsgName={0} Flight={1}".format(msg_id, flight_id))
        self.assertTrue(evt.wait(timeout=3.0), "Range infos are not received")
        IvyUnBindMsg(b_id)
        return range_infos

    def test_range(self):
        """Test the GetRange command"""
        self.assertEqual(self.__get_range("ALL"), {
            "visible": "N/A",
            "f_time": "11:24:00",
            "l_time": "12:33:16",
        })
        # test for one flight
        self.assertEqual(self.__get_range(10001), {
            "visible": "yes",
            "f_time": "11:58:00",
            "l_time": "12:33:16",
        })

    def __get_position(self, flight_id, c_time):
        msg_id = self.test_data.get_random_string()
        evt = Event()
        pos_infos = {}

        def on_position_msg(agent, *larg):
            evt.set()
            pos_infos.update({
                "callsign": larg[0],
                "ssr": larg[1],
                "sector": larg[2],
                "layers": larg[3],
                "x": larg[4],
                "y": larg[5],
                "vx": larg[6],
                "vy": larg[7],
                "fl": larg[8],
                "time": larg[13]
            })

        msg = "Position {0} Flight={1} CallSign=(\S+) Ssr=(\S+) Sector=(\S+) "\
              "Layers=(\S+) X=(\S+) Y=(\S+) Vx=(\S+) Vy=(\S+) Afl=(\S+) "\
              "Rate=(\S+) Heading=(\S+) GroundSpeed=(\S+) Tendency=(\S+) "\
              "Time=(\S+)".format(msg_id, flight_id)
        b_id = IvyBindMsg(on_position_msg, msg)
        # test for all flight
        IvySendMsg("GetPosition MsgName={0} Flight={1} "
                   "Time={2}".format(msg_id, flight_id, c_time))
        self.assertTrue(evt.wait(timeout=3.0), "Pos infos are not received")
        IvyUnBindMsg(b_id)
        return pos_infos

    def test_position(self):
        """Test the GetPosition command"""
        self.assertEqual(self.__get_position(10001, "11:59:55"), {
            'callsign': 'SFA447',
            'y': '-199.05',
            'vx': '-50.00',
            'ssr': '1000',
            'fl': '28',
            'time': '12:00:00',
            'x': '57.38',
            'layers': 'F',
            'vy': '61.00',
            'sector': '--'
        })
