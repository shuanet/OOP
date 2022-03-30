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

import logging
from sqlalchemy import func
from pyrejeu.db.models import MiscInfo
from pyrejeu.db.models import Flight
from pyrejeu.db.models import Cone
from pyrejeu.db.models import Beacon
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.db.models import Layer
from pyrejeu.handlers.base import BaseHandler
from pyrejeu import rpc_decorator


class MiscHandler(BaseHandler):
    """this class handles the misc commands"""
    NAME = "misc"

    def subscribe(self):
        """Subscribe to misc commands"""
        self.set_subscriptions([
            {
                "name": "FileWrite",
                "callback": self.file_write,
                "params": [
                    {"name": "Type", "type": "string"},
                    {"name": "Name", "type": "string"}
                ]
            }, {
                "name": "CancelLastOrder",
                "callback": self.cancel_last_order,
                "params": [{"name": "Flight", "type": "int"}]
            }, {
                "name": "DiscardAll",
                "callback": self.discard_all,
                "params": []
            }, {
                "name": "Discard",
                "callback": self.discard,
                "params": [{"name": "Flight", "type": "int"}]
            }, {
                "name": "Enable",
                "callback": self.enable,
                "params": [{"name": "Flight", "type": "int"}]
            }
        ])

    @rpc_decorator(require_flight=True, commit=True)
    def cancel_last_order(self, session, msg_name, flight):
        """
        Cancel the last order given for the flight identified with <flight_id>

        :param session: the current sqlalchemy session
        :param flight: target flight
        :return: None
        """
        if flight.active_version > 0:
            session.query(Cone).filter(Cone.flight_id == flight.id,
                                       Cone.version == flight.active_version)\
                               .delete(synchronize_session='evaluate')
            flight.active_version -= 1
            # update flight plan
            session.query(FlightPlanBeacon)\
                   .filter(FlightPlanBeacon.flight_plan_id == flight.flight_plan.id,
                           FlightPlanBeacon.version == flight.flight_plan.active_version)\
                   .delete(synchronize_session='fetch')
            flight.flight_plan.active_version -= 1
            self.send_pln_event(flight)
            # send RangeUpdateEvent if necessary
            c_min, c_max = session.query(func.min(Cone.hour),
                                         func.max(Cone.hour)).one()
            current_min, current_max = self._clock.get_cone_range()
            if current_max != c_max or current_min != c_min:
                # update range and send event
                self._clock.send_range_event(session)
            return None
        return self.error(msg_name,
                          "CancelLastOrder: no previous order exists")

    @rpc_decorator(require_flight=True)
    def discard(self, session, msg_name, flight):
        """
        Disable a flight (meaning no events anymore for this flight)

        :param session: the current sqlalchemy session
        :param flight: selected flight
        """
        flight.enabled = False
        flight.last_emitted_cone = -1
        session.commit()

    @rpc_decorator()
    def discard_all(self, session, msg_name):
        """
        Disable all the flight

        :param session: the current sqlalchemy session
        :param flight: selected flight
        """
        session.query(Flight).update({"enabled": False})
        session.commit()

    @rpc_decorator(require_flight=True)
    def enable(self, session, msg_name, flight):
        """
        Enable a flight

        :param session: the current sqlalchemy session
        :param flight: selected flight
        """
        flight.enabled = True
        session.commit()

    @rpc_decorator()
    def file_write(self, session, msg_name, f_type, f_name):
        """
        Save all the database data in a text file

        :param session: the current sqlalchemy session
        :param f_type: format of the output file (only dump supported)
        :param f_name: name of the output file
        """
        # for the moment we only support dump format
        if f_type != "dump":
            logging.error("FileWrite: only dump format is supported")
            return

        try:
            with open(f_name, "w") as f:
                flights = session.query(Flight).all()
                beacons = session.query(Beacon).all()
                layers = session.query(Layer).all()

                f.write(self.__header(session))
                # flight section
                f.write(self.__flight_preamble())
                f.write("NbVols: {0:d}\n".format(len(flights)))
                for flight in flights:
                    f.write(flight.dump()+"\n")
                    f.write(flight.flight_plan.dump()+"\n")
                    f.write("NbPlots: {0:d}\n".format(len(flight.cones)))
                    for cone in flight.cones:
                        f.write(cone.dump()+"\n")
                # beacon section
                f.write(self.__beacon_preamble())
                f.write("NBeacons: {0:d}\n".format(len(beacons)))
                for beacon in beacons:
                    f.write(beacon.dump()+"\n")
                # layer section
                f.write(self.__layer_preamble())
                f.write("NLayers: {0:d}\n".format(len(layers)))
                for layer in layers:
                    f.write(layer.dump()+"\n")
        except IOError:
            logging.error("Unable to create file %s", f_name)

    def __beacon_preamble(self):
        return """########## Beacons
# NOM  X(1/8 NM) Y(1/8 NM)
"""

    def __layer_preamble(self):
        return """########## Layers
# Liste des champs dans l'ordre:
# Name: nom de la couche => 1 caractere
# Floor : Niveau plancher
# Ceiling : Niveau plafond
# Climb_delay_first : combien de temps (minutes) avant la premiere balise de la couche
#               il faut mettre l'avion dans cette couche, quand il y arrive en montant
# Climb_delay_others : non implemente
# Descent_delay : combien de temps (minutes) avant la premiere balise de la couche il faut
#               mettre l'avion dans cette couche, quand il y arrive en descendant
# Descent_Distance: non implemente
"""

    def __flight_preamble(self):
        return """# Fichier genere automatiquement (dump_ast2rej, legal2rej ou rejeu)
# Le premier caractere donne le "type" de ligne :
# # Ceci est un commentaire
# $ FLIGHT HDEB HFIN FL SPEED IVOL AV TERD TERA SSR RVSM TCAS ADSB <-- Mini Plan de Vol
# ! {NOMBAL (V ou A) HEURE_REELLE HEURE_ESTIMEE FL}  <-- Survols balises
# > NOMSECT HENTREE HSORTIE HSTRIP TFL               <-- Infos secteurs
# < FLIGHT {H MINVALIDLEVEL MAXVALIDLEVEL ENDALERT}  <-- Filet de sauvegarde
# % {HEURE TYPE}                                     <-- Alerte relief (MSAW)
# Autre ligne est un mouvement piste correspondant au dernier mini_pln.
# Le nombre de ces lignes est fourni par "NbPlots"
# Un mouvement est compose de:
# HEURE X(1/64 Nm) Y(1/64 Nm) VX(Kts) VY(Kts) FL TAUX(Ft/min) TENDANCE
#
# En fin de fichier: liste des balises, couches, stacks, Ils, Sid/Star connus
"""

    def __header(self, session):
        version = session.query(MiscInfo)\
                         .filter(MiscInfo.name == "version")\
                         .one_or_none()
        centre = session.query(MiscInfo)\
                        .filter(MiscInfo.name == "centre")\
                        .one_or_none()

        header = ""
        if version is not None:
            header += "Version: {0}\n".format(version.value)
        if centre is not None:
            header += "Centre: {0}\n".format(centre.value)
        return header


handler = MiscHandler
