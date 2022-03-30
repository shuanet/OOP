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
import math
import copy
from pyrejeu import PyRejeuBaseObject
from pyrejeu.db.models import FlightPlan
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.utils import str_to_sec
from pyrejeu.utils import min_dist_to_beacon


class BaseHandler(PyRejeuBaseObject):
    NAME = ""

    def __init__(self, bus, db_conn, clock):
        super(BaseHandler, self).__init__(bus, db_conn)
        self._clock = clock

    def close(self):
        pass

    def subscribe(self):
        pass

    def get_origin(self, origin_str):
        origin = None
        if origin_str.lower() == "origin":
            origin = 0
        if origin_str.lower() == "now":
            origin = self._clock.get_current_time_seconds()
        elif re.match("^\d{2}:\d{2}:\d{2}$", origin_str):
            origin = str_to_sec(origin_str)
        elif re.match("^\d{2}:\d{2}$", origin_str):
            origin = str_to_sec(origin_str+":00")

        return origin

    def create_cone(self, c_idx, flight, p_cone, inc_time):
        if c_idx < len(flight.cones):
            if p_cone is not None:
                inc_time = flight.cones[c_idx].hour - p_cone["hour"]
            new_cone = copy.copy(flight.cones[c_idx].__dict__)
            del new_cone["id"]
            new_cone["version"] += 1
            c_idx += 1
        else:
            new_cone = {
                "hour": p_cone["hour"] + inc_time,
                "flight_id": p_cone["flight_id"],
                "version": p_cone["version"]
            }
            self.update_cone_vert(p_cone, new_cone, inc_time)

        return c_idx, inc_time, new_cone

    def update_cone(self, p_cone, new_cone, inc_time, heading):
        # calculate new speed vector
        speed = math.sqrt(p_cone["vit_x"]**2 + p_cone["vit_y"]**2)
        n_vit_x = speed * math.sin(math.radians(heading))
        n_vit_y = speed * math.cos(math.radians(heading))

        # modify trajectory
        new_cone.update({
            "vit_x": n_vit_x,
            "vit_y": n_vit_y,
            "pos_x": p_cone["pos_x"] + inc_time*n_vit_x/3600.0,
            "pos_y": p_cone["pos_y"] + inc_time*n_vit_y/3600.0,
        })

    def update_cone_vert(self, p_cone, new_cone, inc_time):
        c_alt = "alt" in p_cone and p_cone["alt"] \
                                or p_cone["flight_level"] * 1000.0
        alt = c_alt + p_cone["rate"] * inc_time/60.0
        new_cone.update({
            "alt": alt,
            "flight_level": int(alt/1000),
            "rate": p_cone["rate"],
            "tendency": p_cone["tendency"],
        })

    def update_fpl(self, session, flight, hour=None, track=None, event=True):
        fpl_beacons = session.query(FlightPlanBeacon)\
                             .join(FlightPlan)\
                             .filter(FlightPlan.flight_id == flight.id)
        if hour is not None:
            fpl_beacons = fpl_beacons.filter(FlightPlanBeacon.hour <= hour)

        fpl_list = []
        for fpl_beacon in fpl_beacons.all():
            new_b = copy.copy(fpl_beacon.to_dict())
            del new_b["id"]
            new_b["version"] += 1
            if track is not None and fpl_beacon.beacon is not None:
                m_dist, cone = min_dist_to_beacon(track,
                                                  fpl_beacon.beacon.to_dict())
                new_b["V_or_A"] = m_dist < 1.0 and "V" or "A"
                new_b["hour"] = cone["hour"]
            fpl_list.append(new_b)

        if event:
            session.bulk_insert_mappings(FlightPlanBeacon, fpl_list)
            flight.flight_plan.active_version += 1
            session.commit()
            self.send_pln_event(flight)
        return fpl_list

    def send_pln_event(self, flight):
        self.send_event("PlnEvent", [
            ("Flight", flight.id),
            ("Time", self._clock.get_current_time())
        ] + flight.get_pln_attrs())
