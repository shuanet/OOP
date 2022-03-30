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

from pyrejeu import rpc_decorator
from pyrejeu.db.models import Cone
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.db.models import Beacon
from pyrejeu.handlers.base import BaseHandler
from pyrejeu.utils import get_heading
from pyrejeu.utils import dist
from pyrejeu.utils import turn_orientation
from pyrejeu.utils import turn
from pyrejeu.utils import get_heading_to_beacon


class FlightChangeHandler(BaseHandler):
    """this class handles the commands requesting changes about a flight"""
    NAME = "flight_change"

    def subscribe(self):
        """Subscribe to commands requesting a flight modification"""
        self.set_subscriptions([
            {
                "name": "SetPln",
                "callback": self.set_pln,
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "Time", "type": "string"},
                    {"name": "List", "type": "string_list"},
                ]
            }
        ])

    @rpc_decorator(require_flight=True)
    def set_pln(self, session, msg_name, flight, c_time, b_list):
        """
        Change the pln of a flight (SetPln command)

        :param session: the current sqlalchemy session
        :param msg_name: not used
        :param flight: selected flight
        :param time: time at which the fpl modification is asked
        :param b_list: new list of beacons for the flight plan
        """
        s_time = self.get_origin(c_time)
        if s_time is None:
            return self.error(msg_name,
                              "SetPln -- time option has wrong format")

        b_list = b_list.split()
        beacons = session.query(Beacon).filter(Beacon.name.in_(b_list)).all()
        if len(b_list) != len(beacons):
            return self.error(msg_name,
                              "SetPln -- some beacons in List do not exist")
        beacons = [next(b for b in beacons if b.name == b_name)
                   for b_name in b_list]

        # construct the flight plan
        fpl_list = self.update_fpl(session, flight, s_time, event=False)
        fl = len(fpl_list) > 0 and fpl_list[-1]["FL"] or 0
        for beacon in beacons:
            fpl_list.append({
                "beacon_name": beacon.name,
                "beacon": beacon.to_dict(),
                "order": len(fpl_list)+1,
                "V_or_A": "V",
                "FL": fl,
                "hour": 0,
                "estimated_hour": None,
                "flight_plan_id": flight.flight_plan.id,
                "version": flight.flight_plan.active_version+1
            })

        # modify the trajectory
        rate = 3.0
        b_idx, c_idx = len(fpl_list) - len(beacons), 0
        c_heading, t_heading = None, None
        list_cones, p_cone, inc_time = [], None, 8

        while c_idx < len(flight.cones) or b_idx < len(fpl_list) or \
                (list_cones and (list_cones[-1]["hour"] - s_time < 15*60)):
            c_idx, inc_time, new_cone = self.create_cone(c_idx, flight,
                                                         p_cone, inc_time)
            if new_cone["hour"] > s_time and p_cone is not None:
                if b_idx < len(fpl_list):
                    n_bn = fpl_list[b_idx]
                    dist_th = n_bn["V_or_A"] == "A" and 5.0 or 1.0
                    if dist(p_cone, n_bn["beacon"]) < dist_th:
                        # go to the next beacon in the flight pln
                        n_bn["hour"] = new_cone["hour"]
                        b_idx += 1
                    if b_idx < len(fpl_list):
                        b_dict = fpl_list[b_idx]["beacon"]
                        t_heading = get_heading_to_beacon(p_cone, b_dict)
                        if c_heading is not None:
                            by = turn_orientation(c_heading, t_heading)
                            rate = by == "Left" and -rate or rate
                if c_heading is None:
                    c_heading = get_heading(p_cone["vit_x"], p_cone["vit_y"])
                if c_heading != t_heading:
                    c_heading = turn(c_heading, t_heading, rate, inc_time)
                self.update_cone(p_cone, new_cone, inc_time, c_heading)
            list_cones.append(new_cone)
            p_cone = new_cone

        # increment flight version and save
        session.bulk_insert_mappings(Cone, list_cones)
        session.bulk_insert_mappings(FlightPlanBeacon, fpl_list)
        flight.active_version += 1
        flight.flight_plan.active_version += 1
        session.commit()
        # send PlnEvent and TrajectoryEvent
        self.send_pln_event(flight)
        self.send_event("TrajectoryUpdateEvent", [("Flight", flight.id)])
        # send RangeUpdateEvent if necessary
        self._clock.send_range_event(session, list_cones[0]["hour"],
                                     list_cones[-1]["hour"])


handler = FlightChangeHandler
