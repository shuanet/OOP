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

import sys
import os.path
import logging
import time
import re
from sqlalchemy import func
from pyrejeu.db.models import MiscInfo
from pyrejeu.db.models import Flight
from pyrejeu.db.models import Beacon
from pyrejeu.db.models import Cone
from pyrejeu.db.models import FlightPlan
from pyrejeu.db.models import FlightPlanBeacon
from pyrejeu.db.models import Layer
from pyrejeu.utils import str_to_sec, sec_to_str
from pyrejeu.format import Event
from pyrejeu import PyRejeuException


class RejeuImportation(object):
    """
    This class contains all the functions useful to import a file
    following the rejeu format in the database. The public function to import
    a file is import_file
    """

    def __init__(self, bus, db_conn):
        self.db_conn = db_conn
        self.bus = bus

    def import_file(self, filename, event=True):
        """
        This function extract the trafic informations from the rejeu file
        and record them in the database
        :param filename: the path of the file we want to import
        """
        start_time = time.time()
        logging.info("Importation of file %s in progress" % filename)
        logging.info("Please wait...")
        if not os.path.isfile(filename):
            raise PyRejeuException("The file %s does not exist" % filename)
        with open(filename, 'r') as f:
            misc_infos = []
            flights = []
            f_cones = []
            flight_plans = []
            fpl_beacons = []
            beacons = []
            layers, nb_layers = [], 0
            current_flight = None
            current_section = ""

            for line in f:
                if line.startswith("#"):
                    continue
                elif line.startswith("Version:"):
                    # parse version number
                    infos = line.split()
                    misc_infos.append({
                        "name": "version",
                        "value": infos[1]
                    })
                elif line.startswith("Centre:"):
                    # parse centre name
                    infos = line.split()
                    misc_infos.append({
                        "name": "centre",
                        "value": infos[1]
                    })
                elif line.startswith("NBeacons"):
                    current_section = "beacons"
                elif line.startswith("NbPlots"):
                    current_section = "cones"
                elif line.startswith("NLayers"):
                    current_section = "layers"
                    nb_layers = int(line.split()[-1])
                elif line.startswith("$"):
                    current_flight = self.__create_flight_mapping(line)
                    flights.append(current_flight)
                elif line.startswith("!"):
                    if current_flight is None:
                        raise PyRejeuException("Un plan de vol est apparut "
                                               "avant la definition du vol")
                    f_id = current_flight["id"]
                    fpl, f_bea = self.__create_flightplan(f_id, line,
                                                          len(flight_plans),
                                                          len(fpl_beacons))
                    flight_plans.append(fpl)
                    fpl_beacons += f_bea
                elif line.startswith(">"):
                    continue  # infos secteurs non gérés pour le moment
                elif line.startswith("<"):
                    continue  # filet de sauvegarde
                elif line.startswith("%"):
                    continue  # alerte relief
                else:
                    if current_section == "cones":
                        if current_flight is None:
                            raise PyRejeuException("Un plan de vol est"
                                                   "apparut avant la "
                                                   "definition du vol")
                        f_id = current_flight["id"]
                        f_cones.append(self.__create_cone_mapping(f_id, line))
                    elif current_section == "beacons":
                        beacons.append(self.__create_beacon_mapping(line))
                    elif current_section == "layers"\
                            and len(layers) < nb_layers:
                        layers.append(self.__create_layer_mapping(line))

            # alimentation de la base de donnée
            engine = self.db_conn.get_engine()
            engine.execute(MiscInfo.__table__.insert(), misc_infos)
            engine.execute(Beacon.__table__.insert(), beacons)
            if nb_layers > 0:
                engine.execute(Layer.__table__.insert(), layers)
            engine.execute(Flight.__table__.insert(), flights)
            engine.execute(Cone.__table__.insert(), f_cones)
            engine.execute(FlightPlan.__table__.insert(), flight_plans)
            engine.execute(FlightPlanBeacon.__table__.insert(), fpl_beacons)

        stop_time = time.time()
        logging.info("Importation of %d flights in %d seconds !!",
                     len(flights), stop_time - start_time)
        if event:
            self.__send_file_read_event(filename)

    def __send_file_read_event(self, f_name):
        session = self.db_conn.get_session()
        try:
            s_time, e_time = session.query(func.min(Cone.hour),
                                           func.max(Cone.hour)).one()
        except Exception as e:
            logging.error("Unable to get time boundaries: %s", str(e))
            s_time, e_time = 0
        self.bus.publish_event(Event("FileReadEvent", [
            ("Type", "REJEU"),
            ("Name", os.path.basename(f_name)),
            ("StartTime", sec_to_str(s_time)),
            ("EndTime", sec_to_str(e_time))
        ]))
        session.close()

    def __create_layer_mapping(self, l_line):
        l_infos = l_line.split()
        return {
            "name": l_infos[0],
            "floor": int(l_infos[1]),
            "ceiling": int(l_infos[2]),
            "climb_delay_first": int(l_infos[3]),
            "climb_delay_others": int(l_infos[4]),
            "descent_delay": int(l_infos[5]),
            "descent_distance": float(l_infos[6]),
        }

    def __create_beacon_mapping(self, b_line):
        b_infos = b_line.split()
        return {
            "name": b_infos[0],
            "pos_x": int(b_infos[1])/8.0,
            "pos_y": int(b_infos[2])/8.0
        }

    def __create_flight_mapping(self, flight_line):
        flight_infos = flight_line.split()
        # f_id, f_h_dep, f_h_arr, f_fl, f_speed, f_callsign, f_type, f_dep
        # f_arr, ssr, rvsm, tcas, adsb, (dlink)
        f_object = {
            "id": int(flight_infos[1]),
            "fl": int(flight_infos[4]),
            "v": int(flight_infos[5]),
            "callsign": flight_infos[6],
            "type": flight_infos[7],
            "dep": flight_infos[8],
            "arr": flight_infos[9],
            "ssr": flight_infos[10],
            "rvsm": flight_infos[11],
            "tcas": flight_infos[12],
            "adsb": flight_infos[13],
            "dlink": "FALSE",
        }
        # le champ DLINK est optionnel
        if len(flight_infos) > 14:
            f_object["dlink"] = flight_infos[14]
        return f_object

    def __create_cone_mapping(self, flight_id, cone_line):
        cone_infos = cone_line.split()
        # (hour, pos_x, pos_y, vit_x, vit_y, fl, rate, tendency)
        return {
            "flight_id": flight_id,
            "hour": str_to_sec(cone_infos[0]),
            "pos_x": float(cone_infos[1])/64.0,
            "pos_y": float(cone_infos[2])/64.0,
            "vit_x": float(cone_infos[3]),
            "vit_y": float(cone_infos[4]),
            "flight_level": int(cone_infos[5]),
            "rate": int(cone_infos[6]),
            "tendency": cone_infos[7]
        }

    def __create_flightplan(self, flight_id, plan_line, f_idx, b_idx):
        tmp_tab = plan_line.split()
        datas = []
        index = 1
        if (len(tmp_tab)-1) % 5 == 0:
            while index < len(tmp_tab):
                (fp_beacon, V_or_A,
                 fp_hour, es_hour, fp_fl) = tmp_tab[index:index+5]
                if not re.match("^\d{2}:\d{2}:\d{2}$", es_hour):
                    es_hour = None
                else:
                    es_hour = str_to_sec(es_hour)
                datas.append((fp_beacon, V_or_A, fp_hour, es_hour, fp_fl))
                index += 5
        else:
            logging.error("Unable to parse flight plan for flight %s",
                          flight_id)

        flight_plan = {
            "id": f_idx,
            "flight_id": flight_id
        }
        beacons = [{
            "id": b_idx+i,
            "flight_plan_id": f_idx,
            "order": i+1,
            "beacon_name": data[0],
            "V_or_A": data[1],
            "hour": str_to_sec(data[2]),
            "estimated_hour": data[3],
            "FL": data[4]
        } for i, data in enumerate(datas)]
        return flight_plan, beacons


if __name__ == "__main__":
    from pyrejeu.db.connection import DatabaseConnection
    logging.basicConfig(format='%(asctime)-15s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    if len(sys.argv) != 2:
        sys.exit("Usage : importation.py <file>")

    db_conn = DatabaseConnection()
    import_obj = RejeuImportation(db_conn)
    import_obj.import_file(sys.argv[1])

    # Test rapide sur la BDD importee
    print("------------ Test sur la base de données --------------")
    session_test = db_conn.get_session()
    print("Affichage d'une balise")
    print(session_test.query(Beacon).first())
    print("Affichage des informations sur les vols")
    for flight in session_test.query(Flight):
        print(flight)
        print(flight.display_cones_extract())
    print("Affichage des plans de vol")
    for fpl in session_test.query(FlightPlan):
        print(fpl)
