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

from pyrejeutest.base import AmqpPyRejeuTest


class AmqpBusTest(AmqpPyRejeuTest):

    def test_rpc_command(self):
        """Test command without arguments througth AMQP"""
        ans = self.send_command("GetClockDatas")["result"]
        self.assertEqual(ans, {
            'Time': '11:24:00',
            'Rate': '1.0',
            'Bs': '0',
            'Stop': '1'
        })

    def test_rpc_command_args(self):
        """Test command with arguments througth AMQP"""
        ans = self.send_command("GetPosition", args={
            "Flight": 10002,
            "Time": "11:55:05"
        })
        self.assertEqual(ans["result"], {
            'GroundSpeed': 127,
            'Layers': 'F',
            'CallSign': 'SFA438',
            'X': '68.02',
            'Sector': '--',
            'Rate': 0,
            'Flight': 10002,
            'Ssr': '1000',
            'Vx': '-60.00',
            'Vy': '-112.00',
            'Y': '-202.41',
            'Time': '11:55:12',
            'Afl': 80,
            'Heading': 208,
            'Tendency': 0
        })

    def test_rpc_command_missing_args(self):
        """Test that error occurs for command with missing arguments"""
        ans = self.send_command("AircraftDirect", {"Flight": 10001})
        self.assertTrue("error" in ans)
        self.assertEqual(ans["error"]["code"], -32602)

    def test_rpc_complex(self):
        """Test complex command GetDatabaseInfos througth AMQP"""
        cond = "AircraftType=TOBA and Fl=40"
        infos = self.send_command("GetDataBaseInfos", {"Cond": cond})
        self.assertEqual(infos["result"]["List"], "10001")

        infos = self.send_command("GetDataBaseInfos",
                                  {"Cond": cond, "Select": "Ssr"})
        self.assertEqual(infos["result"]["List"], "10001,1000")

    def test_event_receive(self):
        """Test reception of events througth AMQP"""
        self.send_command("ClockStart")

        evt = self.events.get()
        self.assertEqual(evt, "ClockEvent Time=11:24:00 Rate=1.0 Bs=0")
        self.send_command("ClockStop")
        self.send_command("SetClock", {"Time": "11:24:00"})
