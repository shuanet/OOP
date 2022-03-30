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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import relationship
from pyrejeu import utils
from pyrejeu.utils import sec_to_str
from pyrejeu.utils import get_heading
from pyrejeu.utils import get_gs
Base = declarative_base()


class MiscInfo(Base):
    """Table used to record misc informations from rejeu file"""
    __tablename__ = 'misc_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    value = Column(String(128))


class Beacon(Base):
    """Beacon object"""
    __tablename__ = 'beacons'

    id = Column(Integer, primary_key=True)  # Identifiant balise
    name = Column(String(10))               # Nom de la balise
    pos_x = Column(Float)                   # Position de la balise sur l'axe x
    pos_y = Column(Float)                   # Position de la balise sur l'axe y

    def __repr__(self):
        return "<Beacon(name='%s', pos_x=%f, pos_y=%f)>"\
            % (self.name, self.pos_x, self.pos_y)

    def to_dict(self):
        return self.__dict__

    def format(self):
        return "%s %.2f %.2f" % (self.name, self.pos_x, self.pos_y)

    def dump(self):
        return "{0} {1:d} {2:d}".format(self.name, int(self.pos_x*8),
                                        int(self.pos_y*8))


class Flight(Base):
    """Flight object"""
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True)             # Numero de vol
    fl = Column(Integer)                               # Flight level
    v = Column(Integer)                                # Vitesse
    callsign = Column(String(10))                      # Identifiant appel
    type = Column(String(10))                          # Type d avion
    dep = Column(String(10))                           # Aeroport de depart
    arr = Column(String(10))                           # Aeroport d arrivee
    ssr = Column(String(10))                           # Code transpondeur
    rvsm = Column(String(10))                          # equipement rvsm
    tcas = Column(String(10))                          # tcas ou non
    adsb = Column(String(10))                          # adsb ou non
    dlink = Column(String(10))                         # dlink ou non
    # informations utilisées en interne
    enabled = Column(Boolean, default=True)
    pln_event = Column(Boolean, default=False)
    last_emitted_cone = Column(Integer, default=-1)
    active_version = Column(Integer, default=0)

    # déclaration des relations
    flight_plan = relationship("FlightPlan", uselist=False,
                               back_populates="flight")
    cones = relationship("Cone", back_populates="flight", order_by="Cone.hour")

    def __repr__(self):
        return "<Flight(fl={2:d}, v={3:d}, "\
               "callsign={4}, type={5}, dep={6}, arr={7}, "\
               "pln_event={8})>".format(self.fl, self.v, self.callsign,
                                        self.type, self.dep, self.arr,
                                        self.pln_event)

    def get_pln_attrs(self, s_time=0):
        return [
            ("CallSign", self.callsign),
            ("AircraftType", self.type),
            ("Ssr", self.ssr),
            ("Speed", self.v),
            ("Rfl", self.fl),
            ("Dep", self.dep),
            ("Arr", self.arr),
            ("Rvsm", self.rvsm),
            ("Tcas", self.tcas),
            ("Adsb", self.adsb),
            ("Dlink", self.dlink),
            ("List", self.flight_plan.format(s_time))
        ]

    def display_cones_extract(self):
        def repr(c_list):
            return "\n\t".join([str(c) for c in c_list])

        return "\t%s\n\t ... \n\t%s" % (repr(self.cones[0:2]),
                                        repr(self.cones[-3:-1]))

    def dump(self):
        return "$ {0:d} {1} {2} {3:d} {4} {5} {6} {7} {8} {9} {10} {11} "\
               "{12} {13}".format(self.id, sec_to_str(self.cones[0].hour),
                                  sec_to_str(self.cones[-1].hour), self.fl,
                                  self.v, self.callsign, self.type,
                                  self.dep, self.arr, self.ssr, self.rvsm,
                                  self.tcas, self.adsb, self.dlink)


class Cone(Base):
    """Cone object"""
    __tablename__ = 'cones'

    id = Column(Integer, primary_key=True)    # Identifiant du plot
    pos_x = Column(Float)                     # Position sur l'axe x
    pos_y = Column(Float)                     # Position sur l'axe y
    vit_x = Column(Float)                     # Vitesse sur l'axe x
    vit_y = Column(Float)                     # Vitesse sur l'axe y
    flight_level = Column(Integer)            # FL de l'avion
    rate = Column(Float)                      # Vitesse verticale
    tendency = Column(Integer)                # Tendance, montee ou descente
    hour = Column(Integer)                    # Heure d'activation du plot
    # création de clé étrangère (composée) pour le vol
    flight_id = Column(Integer)
    version = Column(Integer, default=0)
    __table_args__ = (ForeignKeyConstraint([flight_id, version],
                                           [Flight.id, Flight.active_version]),
                      {})

    # déclaration des relations
    flight = relationship("Flight", back_populates="cones")

    def __repr__(self):
        return "<Cone(pos_x={0:.2f}, pos_y={1:.2f}, vit_x={2:.2f}, "\
               "vit_y={3:.2f}, flight_level={4:d}, rate={5:.2f}, "\
               "tendency={6:d}, hour={7:d}, "\
               "flight={8:d})>".format(self.pos_x, self.pos_y, self.vit_x,
                                       self.vit_y, self.flight_level,
                                       self.rate, self.tendency,
                                       self.hour, self.flight.id)

    def to_dict(self):
        return self.__dict__

    def get_position_attrs(self):
        heading = get_heading(self.vit_x, self.vit_y)
        g_speed = get_gs(self.vit_x, self.vit_y)
        return [
            ("Flight", self.flight.id),
            ("CallSign", self.flight.callsign),
            ("Ssr", self.flight.ssr),
            ("Sector", "--"),
            ("Layers", "F"),
            ("X", "%.2f" % self.pos_x),
            ("Y", "%.2f" % self.pos_y),
            ("Vx", "%.2f" % self.vit_x),
            ("Vy", "%.2f" % self.vit_y),
            ("Afl", self.flight_level),
            ("Rate", int(self.rate)),
            ("Heading", int(heading)),
            ("GroundSpeed", int(g_speed)),
            ("Tendency", self.tendency),
            ("Time", sec_to_str(self.hour))
        ]

    def format(self, full=False):
        if full:
            return "%s %.2f %.2f %.2f %.2f %d %.2f %d" % (
                                        utils.sec_to_str(self.hour),
                                        self.pos_x, self.pos_y,
                                        self.vit_x, self.vit_y,
                                        self.flight_level, self.rate,
                                        self.tendency)
        else:
            return "%.2f %.2f %s %d" % (self.pos_x, self.pos_y,
                                        utils.sec_to_str(self.hour),
                                        self.flight_level)

    def dump(self):
        return "{0}  {1:d} {2:d} {3:d} {4:d}  {5:d}  {6:d}  "\
               "{7:d}".format(sec_to_str(self.hour), int(self.pos_x*64),
                              int(self.pos_y*64), int(self.vit_x),
                              int(self.vit_y), self.flight_level,
                              int(self.rate), self.tendency)


class FlightPlan(Base):
    """Flight plan object"""
    __tablename__ = 'flightplans'

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    active_version = Column(Integer, default=0)

    # déclaration des relations
    flight = relationship("Flight", back_populates="flight_plan")
    beacons = relationship("FlightPlanBeacon",
                           back_populates="flight_plan",
                           order_by="FlightPlanBeacon.order")

    def __repr__(self):
        res = "<FlightPlan(flight=%d)>" % self.flight.id
        for b in self.beacons:
            res += "\n\t%s" % str(b)
        return res

    def has_beacon(self, beacon_name, current_time):
        for b in self.beacons:
            if b.beacon_name == beacon_name and b.hour > current_time:
                return b
        return None

    def format(self, s_time=0):
        return " ".join([b.format() for b in self.beacons if b.hour >= s_time])

    def dump(self):
        return "! {0}".format(" ".join([b.dump() for b in self.beacons]))


class FlightPlanBeacon(Base):
    __tablename__ = 'flightplan_beacons'

    id = Column(Integer, primary_key=True)
    order = Column(Integer)
    hour = Column(Integer)
    estimated_hour = Column(Integer, nullable=True)
    V_or_A = Column(String)
    FL = Column(Integer)
    beacon_name = Column(String(10), ForeignKey('beacons.name'))
    # composed foreign key creation for the flight plan
    version = Column(Integer, default=0)
    flight_plan_id = Column(Integer)
    __table_args__ = (ForeignKeyConstraint([flight_plan_id, version],
                                           [FlightPlan.id,
                                            FlightPlan.active_version]),
                      {})

    # déclaration des relations
    beacon = relationship("Beacon")
    flight_plan = relationship("FlightPlan", back_populates="beacons")

    def __repr__(self):
        return "<FlightPlanBeacon(order=%d, beacon_name=%s, hour=%d)>" % \
               (self.order, self.beacon_name, self.hour)

    def to_dict(self):
        return self.__dict__

    def format(self):
        return "{0} {1} {2} {3}".format(self.beacon_name, self.V_or_A,
                                        sec_to_str(self.hour, seconds=False),
                                        self.FL)

    def dump(self):
        e_hour = self.estimated_hour is None and "--" \
                                             or sec_to_str(self.estimated_hour)
        return "{0} {1} {2} {3} "\
               "{4}".format(self.beacon_name, self.V_or_A,
                            sec_to_str(self.hour), e_hour, self.FL)


class Layer(Base):
    __tablename__ = 'layer'

    name = Column(String, primary_key=True)     # Name: 1 caractere
    floor = Column(Integer)                     # Floor : Niveau plancher
    ceiling = Column(Integer)                   # Ceiling : Niveau plafond
    # Climb_delay_first : combien de temps (minutes) avant la premiere balise
    # de la couche il faut mettre l'avion dans cette couche,
    # quand il y arrive en montant
    climb_delay_first = Column(Integer)
    climb_delay_others = Column(Integer)        # non implémenté
    # Climb_delay_first : combien de temps (minutes) avant la premiere balise
    # de la couche il faut mettre l'avion dans cette couche,
    # quand il y arrive en descendant
    descent_delay = Column(Integer)
    descent_distance = Column(Float)            # non implémenté

    def __repr__(self):
        return "<Layer(name={0}, floor={1:d}, ceiling={2:d}, "\
               "climb_delay_first={3:d}, climb_delay_others={4:d}, "\
               "descent_delay={5:d}, "\
               "descent_distance={6:f})>".format(self.name, self.floor,
                                                 self.ceiling,
                                                 self.climb_delay_first,
                                                 self.climb_delay_others,
                                                 self.descent_delay,
                                                 self.descent_distance)

    def dump(self):
        return "{0}  {1:d} {2:d}  {3:d}  {4:d}  {5:d}  "\
               "{6:.1f}".format(self.name, self.floor, self.ceiling,
                                self.climb_delay_first,
                                self.climb_delay_others, self.descent_delay,
                                self.descent_distance)
