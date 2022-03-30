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
import logging
from threading import Lock
from sqlalchemy import func
from pyrejeu.utils import sec_to_str
from pyrejeu.utils import str_to_sec
from pyrejeu import rpc_decorator, PyRejeuBaseObject
from pyrejeu.format import Event, RpcResult
from pyrejeu.db.models import Flight
from pyrejeu.db.models import Cone


class RejeuClock(PyRejeuBaseObject):
    TRACK_LIFETIME = 9

    def __init__(self, bus, db_conn):
        super(RejeuClock, self).__init__(bus, db_conn)
        self.running = True
        self.paused = True
        self.rate = 1.0
        self.current_time = 0
        self.__time_lock = Lock()
        # set subscriptions to bus messages
        self.set_subscriptions([
            {"name": "ClockStart", "callback": self.start, "params": []},
            {"name": "ClockStop", "callback": self.stop, "params": []},
            {"name": "ClockForward", "callback": self.forward, "params": []},
            {"name": "ClockBackward", "callback": self.backward, "params": []},
            {
                "name": "GetClockDatas",
                "callback": self.get_clock_datas,
                "params": []
            },
            {
                "name": "SetClock",
                "callback": self.set_clock,
                "params": [{
                    "name": ("Time", "Rate"),
                    "type": "choices",
                }]
            },
        ])
        # record cone range for later use
        self.__update_cone_range()

    def init_current_time(self, start=None):
        self.paused = start is None
        if start is None or start.lower() == 'auto':
            self.current_time = self.cone_min
        elif re.match("^\d{2}:\d{2}:\d{2}$", start):
            self.current_time = str_to_sec(start)
        elif re.match("^\d{2}:\d{2}$", start):
            self.current_time = str_to_sec(start+":00")
        else:
            try:
                self.current_time = int(start)
            except ValueError:
                logging.error("%s is not a readable format "
                              "for start argument", start)
                return False
        return True

    def __update_cone_range(self, session=None):
        close_session = session is None
        if session is None:
            session = self.db_conn.get_session()
        self.cone_min, self.cone_max = session.query(func.min(Cone.hour),
                                                     func.max(Cone.hour)).one()
        if close_session:
            session.close()

    def get_cone_range(self):
        return self.cone_min, self.cone_max

    def send_range_event(self, session, c_min=0, c_max=86400):
        if self.cone_min > c_min or self.cone_max < c_max:
            self.__update_cone_range(session)
            self.send_event("RangeUpdateEvent", [
                ("FirstTime", sec_to_str(self.cone_min)),
                ("LastTime", sec_to_str(self.cone_max))
            ])

    def get_current_time(self):
        return sec_to_str(self.current_time)

    def get_current_time_seconds(self):
        return self.current_time

    def main_loop(self):
        session = self.db_conn.get_session()
        self.send_range_event(session)

        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            self.__time_lock.acquire()
            self.send_event("ClockEvent", [
                ("Time", sec_to_str(self.current_time)),
                ("Rate", "%.1f" % self.rate),
                ("Bs", "0")
            ])

            start_time = time.time()
            cones = session.query(Cone)\
                           .join(Cone.flight)\
                           .filter(Cone.hour == self.current_time,
                                   Flight.enabled.is_(True))
            # envoies de tous les événements et enregistrement des changements
            self.__generate_cones(session, cones)
            self.__generate_events(session)
            self.__send_end_transmission_event()
            session.commit()

            self.current_time += self.rate < 0 and -1 or 1
            self.__time_lock.release()

            task_duration = time.time() - start_time
            sleep_duration = 1.0/abs(self.rate)
            time.sleep(max(0, sleep_duration - task_duration))

        # finally close session
        session.close()

    def __send_end_transmission_event(self):
        self.send_event("EndTransmissionEvent", [
            ("Time", sec_to_str(self.current_time))
        ])

    def __send_pln_event(self, flight, hour):
        self.send_event("PlnEvent", [
            ("Flight", flight.id),
            ("Time", sec_to_str(hour))
        ] + flight.get_pln_attrs())
        flight.pln_event = True

    def __generate_cones(self, session, list_cones):
        for cone in list_cones:
            if not cone.flight.pln_event:
                self.__send_pln_event(cone.flight, cone.hour)
            self.send_event("TrackMovedEvent", cone.get_position_attrs())
            cone.flight.last_emitted_cone = self.current_time

    def __generate_events(self, session):
        # died events
        bound = self.current_time - self.TRACK_LIFETIME
        if bound > 0:
            died_flights = session.query(Flight)\
                                  .filter((Flight.last_emitted_cone != -1) &
                                          (Flight.last_emitted_cone < bound) &
                                          (Flight.enabled.is_(True)))\
                                  .all()
            for flight in died_flights:
                self.send_event("TrackDiedEvent", [("Flight", flight.id)])
                flight.last_emitted_cone = -1
        # TODO beacon events

    @rpc_decorator()
    def stop(self, session, msg_name):
        logging.debug("Clock Stopped")
        self.paused = True

    @rpc_decorator()
    def start(self, session, msg_name):
        logging.debug("Clock Started")
        self.paused = False

    @rpc_decorator()
    def set_clock(self, session, msg_name, key, value):
        if key == "Time":
            if not re.match("^\d{2}:\d{2}:\d{2}$", value):
                return self.error(msg_name, "{0} is not a time".format(value))
            self.modify_time(session, value)
        elif key == "Rate":
            try:
                self.rate = float(value)
            except ValueError:
                return self.error(msg_name, "{0} is not a float".format(value))

    def modify_time(self, session, time):
        self.__time_lock.acquire()
        self.current_time = str_to_sec(time)
        bound = self.current_time - self.TRACK_LIFETIME
        # get flights flying at this time
        flights = session.query(Flight)\
                         .join(Flight.cones)\
                         .filter((Cone.hour <= self.current_time) &
                                 (Cone.hour >= bound) &
                                 (Flight.enabled.is_(True))).all()
        cones = []
        for f in flights:
            cone = session.query(Cone)\
                          .join(Cone.flight)\
                          .filter((Cone.flight == f) &
                                  (Cone.hour <= self.current_time))\
                          .order_by(Cone.hour.desc())\
                          .first()
            cones.append(cone)
        self.__generate_cones(session, cones)
        self.__generate_events(session)
        self.__send_end_transmission_event()
        self.__time_lock.release()
        session.commit()

    @rpc_decorator()
    def forward(self, session, msg_name):
        self.rate = abs(self.rate)

    @rpc_decorator()
    def backward(self, session, msg_name):
        self.rate = -abs(self.rate)

    @rpc_decorator()
    def get_clock_datas(self, session, msg_name):
        return RpcResult(msg_name, "ClockDatas", [
            ("Time", sec_to_str(self.current_time)),
            ("Rate", "%.1f" % self.rate),
            ("Bs", "0"),
            ("Stop", self.paused and "1" or "0")
        ])

    def send_event(self, evt_name, attrs):
        self.bus.publish_event(Event(evt_name, attrs))

    def close(self):
        self.running = False
