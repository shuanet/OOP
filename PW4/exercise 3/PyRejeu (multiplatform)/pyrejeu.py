#!/usr/bin/env python3
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
import os
from optparse import OptionParser
import logging
import signal
import tempfile
from pyrejeu import __version__
from pyrejeu.bus import init_bus_module
from pyrejeu.db.importations import RejeuImportation
from pyrejeu.db.connection import DatabaseConnection
from pyrejeu.clock import RejeuClock
from pyrejeu.handlers import set_handlers
from pyrejeu import utils as ut

logging.basicConfig(format='%(asctime)-15s - %(levelname)s - %(message)s')


if __name__ == "__main__":
    usage = "usage: %prog [options] <rejeu file>"
    parser = OptionParser(usage=usage)
    parser.set_defaults(bus_id="ivy://127.255.255.255:2010", verbose=False,
                        app_name="Rejeu", show_version=False, start=None)
    parser.add_option('-d', '--debug', action='store_true', dest='verbose',
                      help='View debug message.')
    parser.add_option('-v', '--version', action='store_true',
                      dest='show_version',
                      help='View pyrejeu version.')
    parser.add_option('-b', '--bus', type='string', dest='bus_id',
                      help="Bus id (format ivy://@IP:port for IVY | "
                           "zmq://host:rpc_port:evt_port for ZeroMQ  "
                           "default to ivy://127.255.255.255:2010)")
    parser.add_option('-a', '--appname', type='string', dest='app_name',
                      help='Application Name')
    parser.add_option('-s', '--start', type='string', dest='start',
                      help='Start pyrejeu at the specified time'
                           'use auto to start at the first available cone')
    (options, args) = parser.parse_args()

    # show version
    if options.show_version:
        print("PyRejeu {0}".format(__version__))
        sys.exit()
    # log init
    level = logging.INFO
    if options.verbose:
        level = logging.DEBUG
    logging.getLogger().setLevel(level)

    # bus connection
    logging.info("Connexion to the bus")
    bus = init_bus_module(options)
    if bus is None:
        sys.exit(1)
    bus.connect()

    # database creation
    db_file = tempfile.NamedTemporaryFile(prefix="pyrejeu", suffix=".db")
    db_connection = DatabaseConnection(file_path=db_file.name)

    # file importation
    if len(args) != 1 or not os.path.isfile(args[0]):
        sys.exit("Error: Usage pyrejeu [options] <trace_file>")
    import_obj = RejeuImportation(bus, db_connection)
    import_obj.import_file(args[0])

    clock = RejeuClock(bus, db_connection)
    if not clock.init_current_time(options.start):
        bus.close()
        sys.exit(1)
    handlers = set_handlers(bus, db_connection, clock)

    # signal handler
    def handler(signum, frame):
        for hd in handlers:
            hd.close()
        clock.close()
        bus.close()
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    # mainloop launch
    logging.info("PyRejeu is ready")
    try:
        clock.main_loop()
    except Exception:
        logging.error("An error occurs in the main loop, see traceback")
        ut.log_traceback(level="error")
    finally:
        db_file.close()
