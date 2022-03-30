
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

from pyrejeu.db.models import Cone
from pyrejeu.db.models import Beacon
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.db.models import FlightPlan
from pyrejeu.handlers.base import BaseHandler
from pyrejeu.utils import get_heading
from pyrejeu.utils import get_heading_to_beacon
from pyrejeu.utils import turn_orientation
from pyrejeu.utils import turn
from pyrejeu.utils import dist
from pyrejeu import rpc_decorator


class PilotHandler(BaseHandler):
    """ This class handle the trajectory modification required for a given
    flight"""
    NAME = "pilot"

    def __init__(self, bus, db_conn, clock):
        super(PilotHandler, self).__init__(bus, db_conn, clock)
        self.__last_order = None

    def error(self, agent, err):
        self.report_event(agent, "ERROR", self.__last_order, err)
        err = "Unable to handle order {0}: {1}".format(self.__last_order, err)
        return super(PilotHandler, self).error(agent, err)

    def subscribe(self):
        """Subscribe to commands requiring a flight pilot changes"""
        self.set_subscriptions([
            {
                "name": "AircraftTurn",
                "callback": self.aircraft_turn,
                "ivyMsgId": "agent",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "Angle", "type": "string"},
                ]
            }, {
                "name": "AircraftDirect",
                "callback": self.aircraft_direct,
                "ivyMsgId": "agent",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "Beacon", "type": "string"},
                ]
            }, {
                "name": "AircraftHeading",
                "callback": self.aircraft_heading,
                "ivyMsgId": "agent",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "To", "type": "string"},
                    {"name": "By", "type": "string", "optional": True},
                    {"name": "rate", "type": "float", "optional": True}
                ]
            }
        ])

    @rpc_decorator(require_flight=True, commit=True)
    def aircraft_direct(self, session, agent, flight, beacon_name):
        """
        Modify the heading of a flight to go directly to a beacon

        :param session: the current sqlalchemy session
        :param agent: id of the ivy agent that sends the order
        :param flight: target flight
        :param beacon: beacon we want to flight to
        :return: NONE
        """
        self.__last_order = "AircraftDirect|{0}|{1}".format(flight.id,
                                                            beacon_name)
        rate = 3.0
        c_time = self._clock.get_current_time_seconds()
        if beacon_name == "RESUME_PLN":
            f_beacon = session.query(FlightPlanBeacon)\
                              .join(FlightPlanBeacon.flight_plan)\
                              .filter(FlightPlan.flight_id == flight.id,
                                      FlightPlanBeacon.hour > c_time+60)\
                              .first()
            beacon = f_beacon is not None and f_beacon.beacon or None
        else:
            beacon = session.query(Beacon)\
                            .filter(Beacon.name == beacon_name)\
                            .one_or_none()

        if beacon is None:
            return self.error(agent, "UNKNOWN_BEACON")

        beacons = self.__define_beacon_list(session, flight, c_time, beacon)
        b_idx, c_idx = 0, 0
        c_heading, t_heading = None, None
        list_cones, p_cone, inc_time = [], None, 8

        while c_idx < len(flight.cones) or b_idx == 0 or \
                (list_cones and (list_cones[-1]["hour"] - c_time < 15*60)):
            c_idx, inc_time, new_cone = self.create_cone(c_idx, flight,
                                                         p_cone, inc_time)
            if new_cone["hour"] > c_time and p_cone is not None:
                if b_idx < len(beacons):
                    n_bn = beacons[b_idx]
                    dist_th = n_bn["V_or_A"] == "A" and 5.0 or 1.0
                    if dist(p_cone, n_bn["beacon"]) < dist_th:
                        # go to the next beacon in the flight pln
                        n_bn["hour"] = new_cone["hour"]
                        b_idx += 1
                    if b_idx < len(beacons):
                        b_dict = beacons[b_idx]["beacon"]
                        t_heading = get_heading_to_beacon(p_cone, b_dict)
                if c_heading is None:
                    c_heading = get_heading(p_cone["vit_x"], p_cone["vit_y"])
                    by = turn_orientation(c_heading, t_heading)
                    rate = by == "Left" and -abs(rate) or abs(rate)
                if c_heading != t_heading:
                    c_heading = turn(c_heading, t_heading, rate, inc_time)
                self.update_cone(p_cone, new_cone, inc_time, c_heading)
            list_cones.append(new_cone)
            p_cone = new_cone
        self.__record_new_trajectory(session, agent, flight, list_cones)

    @rpc_decorator(require_flight=True, commit=True)
    def aircraft_turn(self, session, agent, flight, angle):
        """
        Modify the heading of a flight to make a turn of the number of
        degrees requested thanks to angle.

        :param session: the current sqlalchemy session
        :param agent: id of the ivy agent that sends the order
        :param flight: target flight
        :param angle: value of the angle
        :return: False if an error occurs
        """
        self.__last_order = "AircraftTurn|{0}|{1}".format(flight.id, angle)
        try:
            angle = float(angle)
        except ValueError:
            return self.error(agent, "WRONG_ANGLE")
        c_time = self._clock.get_current_time_seconds()
        rate = angle < 0 and -3.0 or 3.0
        current_heading, heading = None, None
        list_cones, p_cone, inc_time, c_idx = [], None, 8, 0

        while c_idx < len(flight.cones) or \
                (list_cones and (list_cones[-1]["hour"] - c_time < 15*60)):
            c_idx, inc_time, new_cone = self.create_cone(c_idx, flight,
                                                         p_cone, inc_time)
            if new_cone["hour"] > c_time and p_cone is not None:
                # calculate the heading for this cone
                if current_heading is None:
                    current_heading = get_heading(p_cone["vit_x"],
                                                  p_cone["vit_y"])
                    heading = current_heading + angle
                if current_heading != heading:
                    current_heading = turn(current_heading, heading,
                                           rate, inc_time)
                self.update_cone(p_cone, new_cone, inc_time, current_heading)
            list_cones.append(new_cone)
            p_cone = new_cone
        self.__record_new_trajectory(session, agent, flight, list_cones)

    @rpc_decorator(require_flight=True, commit=True)
    def aircraft_heading(self, session, agent, flight, heading, by=None, rate=1):
        """
        Modify the heading of a flight

        :param session: the current sqlalchemy session
        :param agent: id of the ivy agent that sends the order
        :param flight: target flight
        :param heading: value of the new heading
        :param by: direction of the turn ("None", "Right" or "Left")
        :param rate: turn rate in °/sec
        :return: False if an error occurs
        """
        self.__last_order = "AircraftHeading|{0}|{1}".format(flight.id, heading)
        try:
            rate = 3.0*float(rate)
        except ValueError:
            rate = 3.0
        c_time = self._clock.get_current_time_seconds()
        # parse heading field: must be a number (0-360) or the string maintain
        heading = heading.lower()
        if heading != "maintain":
            try:
                heading = float(heading)
            except ValueError:
                heading = -1
            if heading < 0.0 or heading > 360.0:
                return self.error(agent, "WRONG_HEADING")

        current_heading = None
        list_cones, p_cone, inc_time, c_idx = [], None, 8, 0

        while c_idx < len(flight.cones) or \
                (list_cones and (list_cones[-1]["hour"] - c_time < 15*60)):
            c_idx, inc_time, new_cone = self.create_cone(c_idx, flight,
                                                         p_cone, inc_time)
            if new_cone["hour"] > c_time and p_cone is not None:
                # calculate the heading for this cone
                if current_heading is None:
                    current_heading = get_heading(p_cone["vit_x"],
                                                  p_cone["vit_y"])
                    if heading == "maintain":
                        heading = current_heading
                    by = by or turn_orientation(current_heading, heading)
                    rate = by == "Left" and -abs(rate) or abs(rate)
                if current_heading != heading:
                    current_heading = turn(current_heading, heading,
                                           rate, inc_time)
                self.update_cone(p_cone, new_cone, inc_time, current_heading)
            list_cones.append(new_cone)
            p_cone = new_cone
        self.__record_new_trajectory(session, agent, flight, list_cones)

    def report_event(self, agent, status, order, info="NIL"):
        self.send_event("ReportEvent {0}".format(agent), [
            ("Result", status),
            ("Info", info),
            ("Order", order),
        ])

    def __record_new_trajectory(self, session, agent, flight, list_cones):
        # increment flight version and save new cones
        session.bulk_insert_mappings(Cone, list_cones)
        flight.active_version += 1
        # update flight plan
        self.update_fpl(session, flight, track=list_cones)
        # send trajectory update event
        self.send_event("TrajectoryUpdateEvent", [("Flight", flight.id)])
        # send report event
        self.report_event(agent, "OK", self.__last_order)
        # send RangeUpdateEvent if necessary
        self._clock.send_range_event(session, list_cones[0]["hour"],
                                     list_cones[-1]["hour"])

    def __define_beacon_list(self, session, flight, order_time, beacon):
        beacon_list = [{
            "beacon": beacon.__dict__,
            "hour": None,
            "V_or_A": "V",
        }]
        f_beacon = flight.flight_plan.has_beacon(beacon.name, order_time)
        if f_beacon is not None:
            beacons = session.query(FlightPlanBeacon)\
                             .join(FlightPlanBeacon.flight_plan)\
                             .filter(FlightPlan.flight_id == flight.id,
                                     FlightPlanBeacon.hour > f_beacon.hour)\
                             .all()
            beacon_list += [{
                "beacon": b.beacon.__dict__,
                "hour": b.hour,
                "V_or_A": b.V_or_A
            } for b in beacons]
        return beacon_list


handler = PilotHandler
