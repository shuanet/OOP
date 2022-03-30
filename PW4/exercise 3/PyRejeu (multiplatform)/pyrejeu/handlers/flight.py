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
from sqlalchemy import func
from pyrejeu.db.models import Flight
from pyrejeu.db.models import FlightPlan
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.db.models import Cone
from pyrejeu import rpc_decorator
from pyrejeu.format import RpcListResult, RpcResult
from pyrejeu.handlers.base import BaseHandler
from pyrejeu.utils import str_to_sec
from pyrejeu.utils import sec_to_str


class FlightHandler(BaseHandler):
    """this class handles the commands requesting information about a flight"""
    NAME = "flight"

    def subscribe(self):
        """Subscribe to commands requesting a flight information"""
        self.set_subscriptions([
            {
                "name": "GetPosition",
                "callback": self.get_position,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "Time", "type": "string"}
                ]
            }, {
                "name": "GetPln",
                "callback": self.get_pln,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "From", "type": "string"}
                ]
            }, {
                "name": "GetSectorsInfos",
                "callback": self.get_sectors_infos,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Flight", "type": "int"}
                ]
            }, {
                "name": "GetTrajectory",
                "callback": self.get_trajectory,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "From", "type": "string"}
                ]
            }, {
                "name": "GetTrack",
                "callback": self.get_track,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Flight", "type": "int"},
                    {"name": "From", "type": "string"}
                ]
            }, {
                "name": "GetRange",
                "callback": self.get_range,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Flight", "type": "string"}
                ]
            }
        ])

    @rpc_decorator(require_flight=True)
    def get_position(self, session, msg_name, flight, c_time):
        """
        Get the position of a flight at the given time (GetPosition command)

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param flight: selected flight
        :param time: time at which the position is requested
        """
        if not re.match("^\d{2}:\d{2}:\d{2}$", c_time):
            return self.error(msg_name, "%s is not a time following "
                                        "format HH:MM:SS" % c_time)

        s_time = str_to_sec(c_time)
        cone = session.query(Cone)\
                      .filter(Cone.flight_id == flight.id)\
                      .filter(Cone.hour >= s_time, Cone.hour < s_time+30)\
                      .first()
        if cone is not None:
            return RpcResult(msg_name, "Position", cone.get_position_attrs())
        else:
            err = "No position found for flight %s at %s" % (flight.id, c_time)
            return self.error(msg_name, err)

    @rpc_decorator(require_flight=True)
    def get_pln(self, session, msg_name, flight, from_type):
        """
        Get the flight plan (GetPln command)

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param flight: flight object
        :param from_type: origin|now|time|beacon_name
        """
        start = self.get_origin(from_type)
        if start is None:
            # try to interpret from_type as beacon
            beacon = session.query(FlightPlanBeacon).join(FlightPlan)\
                            .filter(FlightPlan.flight_id == flight.id,
                                    FlightPlanBeacon.beacon_name == from_type)\
                            .first()
            if beacon is None:
                return self.error(msg_name, "GetPln: From has bad format")
            start = beacon.hour

        return RpcResult(msg_name, "Pln", [
            ("Flight", flight.id),
            ("Time", self._clock.get_current_time()),
        ] + flight.get_pln_attrs(start))

    @rpc_decorator(require_flight=True)
    def get_sectors_infos(self, session, msg_name, flight):
        # this command is not handled for the moment
        return RpcResult(msg_name, "SectorInfos", [
            ("Flight", flight.id),
            ("List", "--"),
        ])

    @rpc_decorator(require_flight=False)
    def get_range(self, session, msg_name, flight_id):
        """
        Get the time interval of a flight and its visibility (GetRange command)

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param flight_id: id of the flight, ALL for all flight
        """
        query = session.query(func.min(Cone.hour), func.max(Cone.hour))
        visible = "N/A"

        if flight_id != "ALL":
            flight = session.query(Flight).get(flight_id)
            if flight is None:
                err = "Unable to find flight {0}".format(flight_id)
                return self.error(msg_name, err)
            visible = flight.enabled and "yes" or "no"
            query = query.join(Flight).filter(Cone.flight_id == flight_id)
        f_time, l_time = query.one()
        return RpcResult(msg_name, "Range", [
            ("FirstTime", sec_to_str(f_time)),
            ("LastTime", sec_to_str(l_time)),
            ("Visible", visible),
        ])

    def __gen_trajectory(self, session, msg_name, flight_id, from_type,
                         slice_size, msg_prefix, full):
        start = self.get_origin(from_type)
        if start is None:
            err = "From value %s is not supported" % from_type
            return self.error(msg_name, err)
        cones = session.query(Cone)\
                       .join(Cone.flight)\
                       .filter(Cone.flight_id == flight_id, Cone.hour > start)\
                       .order_by(Cone.hour)\
                       .all()

        return RpcListResult(msg_name, msg_prefix,
                             [c.format(full) for c in cones])

    @rpc_decorator(require_flight=False)
    def get_trajectory(self, session, msg_name, flight_id, from_type):
        """
        Get the trajectory of a flight (GetTrajectory command)

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param flight_id: id of the flight
        :param from_type: origin|now|HH:MM:SS
        """
        return self.__gen_trajectory(session, msg_name, flight_id, from_type,
                                     30, "Trajectory", False)

    @rpc_decorator(require_flight=False)
    def get_track(self, session, msg_name, flight_id, from_type):
        """
        Get the full track of a flight (GetTrack command)

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param flight_id: id of the flight
        :param from_type: origin|now|HH:MM:SS
        """
        return self.__gen_trajectory(session, msg_name, flight_id, from_type,
                                     20, "Track", True)


handler = FlightHandler
