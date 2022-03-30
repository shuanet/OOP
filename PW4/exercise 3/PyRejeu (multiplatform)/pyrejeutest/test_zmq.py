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

from pyrejeutest.base import ZmqPyRejeuTest


class ZmqBusTest(ZmqPyRejeuTest):

    def test_rpc_command(self):
        """Test command without arguments througth ZMQ"""
        ans = self.send_command("GetClockDatas")["result"]
        self.assertEqual(ans, {
            'Time': '11:24:00',
            'Rate': '1.0',
            'Bs': '0',
            'Stop': '1'
        })

    def test_rpc_command_args(self):
        """Test command with arguments througth ZMQ"""
        beacons = self.get_all_beacons()
        self.assertEqual(beacons[0], 'MAKOX 52.38 -99.62')

    def test_rpc_command_missing_args(self):
        """Test that error occurs for command with missing arguments"""
        ans = self.send_command("AircraftDirect", {"Flight": 10001})
        self.assertTrue("error" in ans)
        self.assertEqual(ans["error"]["code"], -32602)

    def test_rpc_complex(self):
        """Test complex command GetDatabaseInfos througth ZMQ"""
        cond = "AircraftType=TOBA and Fl=40"
        infos = self.send_command("GetDataBaseInfos", {"Cond": cond})
        self.assertEqual(infos["result"]["List"], "10001")

        infos = self.send_command("GetDataBaseInfos",
                                  {"Cond": cond, "Select": "Ssr"})
        self.assertEqual(infos["result"]["List"], "10001,1000")

    def test_event_receive(self):
        """Test reception of events througth ZMQ"""
        self.record_events()
        self.send_command("ClockStart")

        evt = self.get_event()
        self.assertEqual(evt, "ClockEvent Time=11:24:00 Rate=1.0 Bs=0")
        self.send_command("ClockStop")
        self.send_command("SetClock", {"Time": "11:24:00"})
