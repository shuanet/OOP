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
import re
from threading import Event
from ivy.std_api import IvyBindMsg, IvyUnBindMsg, IvySendMsg
from pyrejeutest.base import IvyPyRejeuTest


class DatabaseReadingTest(IvyPyRejeuTest):
    """
    Test case used to validate that pyrejeu answer
    correcly to database solicitations
    """

    def test_current_flights(self):
        """Test the GetCurrentFlights command"""
        msg_id = self.test_data.get_random_string()
        evt = Event()
        flights = []

        def on_flights_msg(agent, t_value, fl_list):
            flights.extend(fl_list.split())
            evt.set()
        b_id = IvyBindMsg(on_flights_msg, "CurrentFlights {0} Time=(\S+) "
                          "List=(.*)".format(msg_id))
        msg = "GetCurrentFlights MsgName={0} Time=11:24:50".format(msg_id)
        IvySendMsg(msg)
        self.assertTrue(evt.wait(timeout=3.0), "Flight list is not received")
        IvyUnBindMsg(b_id)
        self.assertEqual(flights, ["10002"])

    def test_all_beacons(self):
        """Test the GetAllBeacons command"""
        beacons = self.get_all_beacons()
        self.assertEqual(len(beacons), 1850)
        self.assertEqual(beacons[1], {
            "name": "LFBV",
            "pos_x": 62.0,
            "pos_y": -110.0,
        })
        b_names = [b["name"] for b in beacons]
        self.assertTrue("TH32L" in b_names)

    def test_all_beacons_pilot(self):
        beacons = self.get_all_beacons(t="Pilot")
        self.assertEqual(len(beacons), 1758)
        b_names = [b["name"] for b in beacons]
        self.assertTrue("TH32L" not in b_names)

    def test_beacons_infos(self):
        """Test the GetBeaconsInfos command"""
        r_string = self.test_data.get_random_string()
        b_list = ["LFBO", r_string]
        self.assertEqual(self.get_beacons(b_list), [{
            "name": "LFBO",
            "pos_x": 59.0,
            "pos_y": -201.0,
        }, {
            "name": r_string,
            "pos_x": 0.0,
            "pos_y": 0.0
        }])

    def __get_database_infos(self, cond, select=None):
        msg_id = self.test_data.get_random_string()
        evt = Event()
        database_infos = []

        def on_database_msg(agent, nb, fl_list):
            database_infos.extend(fl_list.split())
            evt.set()

        b_id = IvyBindMsg(on_database_msg, "DataBaseInfos {0} Nb=(\S+) "
                          "List=(.*)".format(msg_id))
        msg = "GetDataBaseInfos MsgName={0} Cond={1}".format(msg_id, cond)
        if select is not None:
            msg += " Select={0}".format(select)
        IvySendMsg(msg)
        self.assertTrue(evt.wait(timeout=3.0), "Db infos are not received")
        IvyUnBindMsg(b_id)
        return database_infos

    def test_database_infos(self):
        """Test the GetDataBaseInfos command"""
        cond = "AircraftType=TOBA and Fl=40"
        infos = self.__get_database_infos(cond)
        self.assertEqual(infos, ["10001"])

        # test with the select option
        cond = "Dep=LFCR and Arr=LFBO"
        infos = self.__get_database_infos(cond, select="Fl,Ssr")
        self.assertEqual(infos, ["10002,80,1000"])

    def test_database_infos_beacon(self):
        """Test the GetDataBaseInfos command with beacon condition"""
        cond = "Ssr=1000 and Beacon=AGN"
        infos = self.__get_database_infos(cond)
        self.assertEqual(infos, ["10001"])

        cond = "AircraftType=TOBA and (Beacon=AGN or Beacon=GAI)"
        infos = self.__get_database_infos(cond, select="Fl,Arr")
        self.assertEqual(infos, ['10001,40,LFBR', "10002,80,LFBO"])

    def test_database_infos_wildcard(self):
        """Test the GetDataBaseInfos command with wildcard caracters"""
        cond = "Ssr=10*"
        infos = self.__get_database_infos(cond)
        self.assertEqual(infos, ["10001", "10002"])

        cond = "AircraftType=TOBA and Beacon=GA*"
        infos = self.__get_database_infos(cond, select="Fl,Arr")
        self.assertEqual(infos, ["10002,80,LFBO"])

        cond = "Ssr=10?"
        infos = self.__get_database_infos(cond)
        self.assertEqual(infos, [])

    def __set_new_beacons(self, beacons_list):
        evt = Event()
        beacon_infos = []

        def on_beacon_evt(agent, b_list):
            r_exp = r"([a-zA-Z\d]{1,5}) (-?\d+\.?\d+?) (-?\d+\.?\d+?)"
            beacon_infos.extend(re.findall(r_exp, b_list))
            evt.set()

        b_id = IvyBindMsg(on_beacon_evt, "BeaconUpdateEvent List=(.*)")
        msg = "SetNewBeacons List={0}".format(beacons_list)
        IvySendMsg(msg)
        self.assertTrue(evt.wait(timeout=3.0), "Beacon evt are not received")
        IvyUnBindMsg(b_id)

        return beacon_infos

    def test_set_new_beacons(self):
        """Test SetNewBeacons command"""
        beacons_list = "ZOU -60.0 150.0 UUU 80.5 -135.4"
        beacon_infos = self.__set_new_beacons(beacons_list)
        # do verification on the result
        self.assertEqual(beacon_infos, [
            ("ZOU", "-60.0", "150.0"),
            ("UUU", "80.5", "-135.4")
        ])
        self.assertEqual(self.get_beacons(["ZOU", "UUU"]), [{
            "name": "ZOU",
            "pos_x": -60.0,
            "pos_y": 150.0,
        }, {
            "name": "UUU",
            "pos_x": 80.5,
            "pos_y": -135.4
        }])

    def test_set_new_beacons_error(self):
        """Test SetNewBeacons command with wrong input"""
        beacons_list = "ZOUUUU -60.0 150.0"
        msg = "SetNewBeacons List={0}".format(beacons_list)
        IvySendMsg(msg)
        time.sleep(0.1)
        # do verification on the result
        self.assertEqual(self.get_beacons(["ZOUUUU"]), [{
            "name": "ZOUUUU",
            "pos_x": 0.0,
            "pos_y": 0.0
        }])
