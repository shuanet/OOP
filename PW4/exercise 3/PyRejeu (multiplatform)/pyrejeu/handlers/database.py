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
from sqlalchemy import func, and_
from pyrejeu.db.models import Beacon
from pyrejeu import rpc_decorator
from pyrejeu.handlers.base import BaseHandler
from pyrejeu.db.filter import translate_filter
from pyrejeu.db.models import Flight
from pyrejeu.db.models import Cone
from pyrejeu.db.models import FlightPlan
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.format import RpcResult, RpcListResult
from pyrejeu.utils import sec_to_str


class DatabaseHandler(BaseHandler):
    """ Cette classe permet de gérer tous les requêtes demandant
        des informations contenues dans la base de donnée"""
    NAME = "database"
    KEYWORDS_TRANSLATION = {
        "AircraftType": "type",
        "Fl": "fl",
        "CallSign": "callsign",
        "Speed": "v",
        "Arr": "arr",
        "Dep": "dep",
        "Ssr": "ssr",
        "Rvsm": "rvsm",
        "Tcas": "tcas",
        "Adsb": "adsb",
        "Dlink": "dlink"
    }

    def subscribe(self):
        """Subscribe to commands requesting database information"""
        self.set_subscriptions([
            {
                "name": "GetAllBeacons",
                "callback": self.get_all_beacons,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Type", "type": "string"}
                ]
            }, {
                "name": "GetBeaconsInfos",
                "callback": self.get_beacons_infos,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "NullCoord", "type": "string"},
                    {"name": "List", "type": "string_list"}
                ]
            }, {
                "name": "SetNewBeacons",
                "callback": self.set_new_beacons,
                "ivyMsgId": "none",
                "params": [{"name": "List", "type": "string_list"}]
            }, {
                "name": "GetCurrentFlights",
                "callback": self.get_current_flights,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Time", "type": "string"}
                ]
            }, {
                "name": "GetDataBaseInfos",
                "callback": self.get_database_infos,
                "ivyMsgId": "MsgName",
                "params": [
                    {"name": "Cond", "type": "string_list"},
                    {"name": "Select", "type": "string", "optional": True},
                ]
            },
        ])

    @rpc_decorator()
    def get_current_flights(self, session, msg_name, t_value):
        """
        Return the list of existing flights at the specified time

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param t_value: the specified time now|HH:MM:SS
        """
        t_value = self.get_origin(t_value)
        if t_value is None:
            err = "Time value is not correct"
            return self.error(msg_name, err)

        flights = session.query(Flight.id).join(Flight.cones)\
                         .filter(Flight.enabled.is_(True))\
                         .group_by(Flight.id)\
                         .having(and_(func.min(Cone.hour) < t_value,
                                      func.max(Cone.hour) > t_value))\
                         .all()
        return RpcResult(msg_name, "CurrentFlights", [
            ("Time", sec_to_str(t_value)),
            ("List", " ".join([str(id) for (id,) in flights])),
        ])

    @rpc_decorator()
    def get_all_beacons(self, session, msg_name, r_type):
        """
        Return the position of all known beacons

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param r_type: the type of beacon Pilot|All
        """
        beacons = session.query(Beacon).all()
        if r_type == "Pilot":
            r_exp = re.compile(r'^[A-Za-z]{2,5}$')
            beacons = [b for b in beacons if r_exp.match(b.name) is not None]

        return RpcListResult(msg_name, "AllBeacons",
                             [b.format() for b in beacons], slice_size=50)

    @rpc_decorator()
    def get_beacons_infos(self, session, msg_name, null_coord, b_list):
        """
        Return the position of beacons given in a list

        :param session: the current sqlalchemy session
        :param null_coord: the string to use for unknown beacon
        :param b_list: the list of beacons
        """
        b_list = b_list.split()
        beacons = session.query(Beacon).filter(Beacon.name.in_(b_list)).all()
        beacons = dict([(b.name, b.format()) for b in beacons])

        f_list = []
        for b_name in b_list:
            try:
                f_list.append(beacons[b_name])
            except KeyError:
                f_list.append("{0} {1} {1}".format(b_name, null_coord))
        return RpcResult(msg_name, "BeaconsInfos", [
            ("List", " ".join(f_list))
        ])

    @rpc_decorator()
    def get_database_infos(self, session, msg_name, cond, select=None):
        """
        Return flights respecting some conditions

        :param session: the current sqlalchemy session
        :param msg_name: the message identifier
        :param cond: the filter condition
        :param select: the list of information to return
        """
        flight_filter = True
        select_attrs = ["id"]
        if cond != "ALL_FLIGHTS":
            try:
                flight_filter = translate_filter(cond)
            except RuntimeError as err:
                err_msg = "GetDabaseInfos -- unable to parse Cond: %s" % err
                return self.error(msg_name, err_msg)
        if select is not None:
            select = select.split(",")
            select_attrs.extend([self.KEYWORDS_TRANSLATION[s] for s in select
                                 if s in self.KEYWORDS_TRANSLATION])

        def format(flight):
            return ",".join([str(getattr(flight, a)) for a in select_attrs])
        query = session.query(Flight)
        if cond.find("Beacon") != -1:
            query = query.join(FlightPlan).join(FlightPlanBeacon)
        flights = query.filter(flight_filter).all()

        return RpcResult(msg_name, "DataBaseInfos", [
            ("Nb", len(flights)),
            ("List", " ".join([format(f) for f in flights]))
        ])

    @rpc_decorator()
    def set_new_beacons(self, session, msg_name, b_list):
        """
        Record new beacons in the database (SetNewBeacons command)

        :param session: the current sqlalchemy session
        :param b_list: list of beacons to add in the db
        """
        r_exp = r"([a-zA-Z\d]{1,5}) (-?\d+\.?\d+?) (-?\d+\.?\d+?)"
        full_regexp = r"(%s)+" % r_exp
        if re.match(full_regexp, b_list) is None:
            err = "SetNewBeacons: '%s' is not a valid list" % b_list
            return self.error(msg_name, err)

        beacons = re.findall(r_exp, b_list)
        beacon_list = [{
                "name": name,
                "pos_x": float(x),
                "pos_y": float(y)
        } for name, x, y in beacons]
        session.bulk_insert_mappings(Beacon, beacon_list)
        session.commit()

        # send BeaconUpdateEvent as answer
        def b_ft(b):
            return "{0} {1} {2}".format(*b)
        self.send_event("BeaconUpdateEvent", [
            ("List", " ".join([b_ft(b) for b in beacons]))
        ])


handler = DatabaseHandler
