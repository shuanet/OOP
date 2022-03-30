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
from pyrejeu.db.filter import translate_filter


class DatabaseFilterTest(unittest.TestCase):
    """
    Test case used to validate that database filter
    used for GetDatabaseInfos command
    """

    def test_basic_filters(self):
        filters = [
            ("Fl < 120", "flights.fl < :fl_1"),
            ("Speed > 100", "flights.v > :v_1"),
            ("Arr = LFBO", "flights.arr = :arr_1"),
        ]
        for f, r in filters:
            self.assertEqual(str(translate_filter(f)), r)

    def test_combined_filters(self):
        f = "Fl > 120 and (AircraftType = A320 or CallSign = AF437)"
        self.assertEqual(str(translate_filter(f)),
                         "flights.fl > :fl_1 AND "
                         "(flights.type = :type_1 "
                         "OR flights.callsign = :callsign_1)")
        f = "(Fl = 80 or Fl < 20) and AircraftType = A320"
        self.assertEqual(str(translate_filter(f)),
                         "(flights.fl = :fl_1 OR flights.fl < :fl_2) "
                         "AND flights.type = :type_1")

    def test_not_filters(self):
        f = "Fl > 120 and not (AircraftType = A320 or Rvsm = True)"
        self.assertEqual(str(translate_filter(f)),
                         "flights.fl > :fl_1 AND NOT "
                         "(flights.type = :type_1 OR flights.rvsm = :rvsm_1)")
        f = "not Fl = 120"
        self.assertEqual(str(translate_filter(f)), "flights.fl != :fl_1")

    def test_beacon_filters(self):
        f = "Ssr=1000 or Beacon=AGN"
        self.assertEqual(str(translate_filter(f)),
                         "flights.ssr = :ssr_1 OR "
                         "flightplan_beacons.beacon_name = :beacon_name_1")

    def test_wildcard_filters(self):
        f = "AircraftType=A*"
        self.assertEqual(str(translate_filter(f)), "flights.type LIKE :type_1")

        f = "Arr=LFB?"
        self.assertEqual(str(translate_filter(f)), "flights.arr LIKE :arr_1")

        f = "Ssr=100?"
        self.assertEqual(str(translate_filter(f)), "flights.ssr LIKE :ssr_1")