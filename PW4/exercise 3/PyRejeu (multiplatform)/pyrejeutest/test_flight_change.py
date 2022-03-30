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

import re
import time
from pyrejeutest.base import IvyPyRejeuTest
from ivy.std_api import IvySendMsg
from pyrejeu.utils import min_dist_to_beacon
from pyrejeu.utils import str_to_sec


class FlightChangeTest(IvyPyRejeuTest):
    """
    Test case used to validate that pyrejeu answer
    correcly to flight modification solicitations
    """

    def __parse_traj(self, trajectory):
        trajectory = re.findall(r"\S+ \S+ \S+ \S+", trajectory)
        trajectory = [t.split() for t in trajectory]
        return [{
            "hour": str_to_sec(hour),
            "pos_x": float(x),
            "pos_y": float(y),
            "fl": int(fl)
        } for x, y, hour, fl in trajectory]

    def test_set_pln(self):
        """Test the SetPln command"""
        f_id = 10001
        b_list = ["GAI", "AGN"]
        beacons = self.get_beacons(b_list)

        IvySendMsg("SetClock Time=12:06:00")
        time.sleep(0.1)
        IvySendMsg("SetPln Flight={0} Time=12:06:00 "
                   "List={1}".format(f_id, " ".join(b_list)))
        time.sleep(0.1)
        trajectory = self.__parse_traj(self.get_trajectory(f_id))
        for beacon in beacons:
            dist, cone = min_dist_to_beacon(trajectory, beacon)
            self.assertTrue(dist < 1.0)

        new_pln = self.get_pln(f_id)
        f_beacons = re.findall(r"\S+ \S+ \S+ \S+", new_pln["List"])
        f_beacons = [b.split()[0] for b in f_beacons]
        self.assertEqual(f_beacons, ["LFBO", "TOU"] + b_list)

        # reset change
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))
